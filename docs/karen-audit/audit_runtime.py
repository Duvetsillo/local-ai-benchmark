"""Bounded read-only diagnostics. Does not record voice, download models, or edit Karen."""
from pathlib import Path
import argparse, ast, hashlib, importlib, importlib.metadata, json, os, subprocess, sys, time

ROOT=Path(r'C:\Karen')
REPORT=Path(__file__).parent
result={'python':sys.version,'executable':sys.executable,'checks':{}}
sys.path.insert(0,str(ROOT))

def check(name,fn):
    start=time.monotonic()
    try: result['checks'][name]={'ok':True,'data':fn(),'seconds':round(time.monotonic()-start,2)}
    except Exception as e: result['checks'][name]={'ok':False,'error':type(e).__name__+': '+str(e),'seconds':round(time.monotonic()-start,2)}
    print(name+': '+('OK' if result['checks'][name]['ok'] else result['checks'][name]['error']),flush=True)

def imports():
    packages={'numpy':'numpy','requests':'requests','sounddevice':'sounddevice','speech_recognition':'SpeechRecognition','pyaudio':'PyAudio','whisper':'openai-whisper','onnxruntime':'onnxruntime','openwakeword':'openwakeword','edge_tts':'edge-tts','soundfile':'soundfile','pyttsx3':'pyttsx3','torch':'torch','tkinter':None}
    out={}
    for mod,dist in packages.items():
        try:
            imported=importlib.import_module(mod)
            out[mod]={'imported':True,'version':importlib.metadata.version(dist) if dist else str(getattr(imported,'TkVersion','available'))}
        except Exception as e: out[mod]={'imported':False,'error':type(e).__name__+': '+str(e)}
    return out

def syntax():
    return {p.name: {'parseable':bool(ast.parse(p.read_text(encoding='utf-8-sig'))),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in ROOT.glob('*.py')}

def configcheck():
    from config import KarenConfig,load_config
    cfg=load_config()
    invalid=[]
    for kwargs in ({'server':'not-a-url'},{'sample_rate':0},{'wake_word_threshold':0}):
        try: KarenConfig(**kwargs); invalid.append(False)
        except ValueError: invalid.append(True)
    assert all(invalid)
    overridden=load_config({'server':'http://127.0.0.1:11434','model':'audit-test'})
    assert overridden.server=='http://127.0.0.1:11434' and overridden.model=='audit-test'
    return {'server':cfg.server,'model':cfg.model,'api_key_present':bool(cfg.api_key),'input_device':cfg.input_device,'whisper_model':cfg.whisper_model,'wake_word_enabled':cfg.wake_word_enabled,'invalid_values_rejected':all(invalid),'overrides_work':True,
            'dotenv_file_present':(ROOT/'.env').exists(),'dotenv_loaded_in_source':'load_dotenv' in (ROOT/'config.py').read_text(encoding='utf-8')}

def cli():
    tree=ast.parse((ROOT/'cliente.py').read_text(encoding='utf-8-sig'))
    fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='parse_args')
    namespace={'argparse':argparse}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'cliente.py','exec'),namespace)
    old=sys.argv[:];out={}
    try:
        for label,argv in [('documented_flags',['--server','http://127.0.0.1:11434','--model','audit-test']),('launcher_flags',['--whisper-model','tiny']),('manual_activation',['--no-wake-word']),('device_flag',['--input-device','4'])]:
            sys.argv=['cliente.py']+argv
            try:
                args=namespace['parse_args']();out[label]={'accepted':True,'arguments':vars(args)}
            except SystemExit as e:out[label]={'accepted':False,'exit_code':e.code}
    finally:sys.argv=old
    return out

def audio_devices():
    import sounddevice as sd
    devices=sd.query_devices()
    entries=[{'index':i,'name':d['name'],'input_channels':d['max_input_channels'],'sample_rate':d['default_samplerate'],'hostapi':d['hostapi']} for i,d in enumerate(devices) if d['max_input_channels']>0]
    proposed=None
    if isinstance(devices,list):
        for i,d in enumerate(devices):
            if d['max_input_channels']>0 and any(x in d['name'].lower() for x in ('microphone','headset','usb audio')):proposed=i;break
    valid=[]
    # Check format compatibility only. Do not open or record the microphone.
    for d in entries:
        try:sd.check_input_settings(device=d['index'],channels=1,dtype='int16',samplerate=16000);valid.append(d['index'])
        except Exception:pass
    return {'collection_type':type(devices).__name__,'is_list':isinstance(devices,list),'inputs':entries,'valid_16khz_inputs':valid,'detector_selected_index':proposed,'default_input':int(sd.default.device[0]),'recording_performed':False}

def onnx():
    import onnxruntime as ort
    import numpy as np
    path=ROOT/'karen.onnx'
    sess=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
    ins=[{'name':x.name,'shape':x.shape,'type':x.type} for x in sess.get_inputs()]
    outs=[{'name':x.name,'shape':x.shape,'type':x.type} for x in sess.get_outputs()]
    synthetic=None
    if len(ins)==1 and ins[0]['type']=='tensor(float)':
        shape=[d if isinstance(d,int) and d>0 else 1 for d in ins[0]['shape']]
        outputs=sess.run(None,{ins[0]['name']:np.zeros(shape,dtype=np.float32)})
        synthetic=[{'shape':list(x.shape),'finite':bool(np.isfinite(x).all()),'min':float(x.min()),'max':float(x.max())} for x in outputs]
    return {'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'providers':sess.get_providers(),'inputs':ins,'outputs':outs,'synthetic_zero_output':synthetic,'real_wake_word_tested':False}

def whisper_cache():
    paths=[Path.home()/'.cache/whisper',ROOT/'models']
    return {str(p):[{'name':f.name,'bytes':f.stat().st_size} for f in p.glob('*.pt')] if p.exists() else [] for p in paths}

def binaries():
    out={}
    for name in ('ffmpeg.exe','ffprobe.exe'):
        proc=subprocess.run([str(ROOT/name),'-version'],capture_output=True,text=True,timeout=10)
        out[name]={'returncode':proc.returncode,'version':proc.stdout.splitlines()[:1]}
    samples=[]
    for path in list(ROOT.glob('*.wav'))+list(ROOT.glob('*.mp3')):
        proc=subprocess.run([str(ROOT/'ffprobe.exe'),'-v','error','-show_entries','format=duration:stream=codec_name,sample_rate,channels','-of','json',str(path)],capture_output=True,text=True,timeout=10)
        samples.append({'name':path.name,'returncode':proc.returncode,'metadata':json.loads(proc.stdout) if proc.returncode==0 else {'error':'ffprobe failed'}})
    out['existing_samples']=samples
    return out

def endpoints():
    import requests
    from config import load_config
    cfg=load_config()
    bases=list(dict.fromkeys([cfg.server,'http://127.0.0.1:11434','http://192.168.100.66:11434','http://192.168.100.66:5000']))
    out=[]
    for base in bases:
        if base.endswith(':5000'): paths=['/salud','/health']
        else:paths=['/api/version','/api/tags']
        for path in paths:
            entry={'base':base,'path':path}
            headers={'Authorization':'Bearer '+cfg.api_key} if cfg.api_key and base==cfg.server else {}
            try:
                start=time.monotonic()
                r=requests.get(base.rstrip('/')+path,headers=headers,timeout=(3,5),allow_redirects=False)
                entry.update({'status':r.status_code,'seconds':round(time.monotonic()-start,2),'content_type':r.headers.get('Content-Type','')})
                try:
                    payload=r.json()
                    entry['json_object']=isinstance(payload,dict)
                    if isinstance(payload,dict):
                        entry['version']=payload.get('version')
                        entry['keys']=sorted(payload.keys())
                        if isinstance(payload.get('models'),list):entry['models']=[{'name':m.get('name'),'bytes':m.get('size')} for m in payload['models'] if isinstance(m,dict)]
                except ValueError:entry['json_object']=False
            except Exception as e:entry['error']=type(e).__name__ # Avoid echoing credentials or network response bodies.
            out.append(entry)
    return out

def gui():
    from config import load_config
    from cliente import KarenApp
    app=KarenApp(load_config({'server':'http://audit.invalid:11434','api_key':''}))
    app.root.withdraw();app.root.update_idletasks()
    info={'constructed':True,'title':app.root.title(),'mic_index':app.mic_index,'mic_button_state':str(app.mic_button['state']),'fields':list(app.fields),'api_key_masked':bool(app.fields['api_key']['show']),'geometry':app.root.geometry()}
    app.fields['server'].delete(0,'end');app.fields['server'].insert(0,'http://127.0.0.1:11434')
    old=app.config.server;app.save_config()
    info.update({'client_target_changes':app.client.server=='http://127.0.0.1:11434','config_object_updated':app.config.server==app.client.server,'original_config_server':old,'listening_started':app.is_listening})
    app.root.destroy()
    return info

def generations():
    import requests
    from config import load_config
    from cliente import KarenClient
    cfg=load_config();out={}
    current=KarenClient(cfg.server,cfg.api_key,cfg.model)
    ok,payload=current.test_connection()
    out['current_connection_test']={'reports_ok':ok,'label':payload.get('label'),'payload_keys':sorted(payload.get('payload',{}).keys())}
    # A tiny synthetic prompt verifies inference without sending personal content.
    for label,base,model in [('current_config',cfg.server,cfg.model),('pc_local','http://127.0.0.1:11434','qwen2:0.5b'),('homelab_ollama','http://192.168.100.66:11434','llama3.2:3b')]:
        start=time.monotonic();entry={'base':base,'model':model}
        headers={'Authorization':'Bearer '+cfg.api_key} if cfg.api_key and label=='current_config' else {}
        try:
            r=requests.post(base+'/api/generate',json={'model':model,'prompt':'Responde solamente OK.','stream':False,'think':False,'keep_alive':'30s','options':{'num_predict':8,'temperature':0}},headers=headers,timeout=(3,45))
            entry.update({'status':r.status_code,'seconds':round(time.monotonic()-start,2),'content_type':r.headers.get('Content-Type','')})
            try:
                data=r.json();entry.update({'valid_response':isinstance(data,dict) and isinstance(data.get('response'),str),'response':data.get('response') if isinstance(data,dict) else None,'done':data.get('done') if isinstance(data,dict) else None,'error':data.get('error') if isinstance(data,dict) else None})
            except ValueError:entry['valid_response']=False
        except Exception as e:entry.update({'error':type(e).__name__,'seconds':round(time.monotonic()-start,2)})
        out[label]=entry
        print(label+': '+str(entry.get('status',entry.get('error'))),flush=True)
    return out

def local_stt():
    import torch, whisper
    torch.set_num_threads(2)
    weights=Path.home()/'.cache/whisper/base.pt'
    sample=ROOT/'muestra_friday_dalia.mp3'
    assert weights.exists() and sample.exists()
    os.environ['PATH']=str(ROOT)+os.pathsep+os.environ.get('PATH','')
    model=whisper.load_model(str(weights),device='cpu')
    response=model.transcribe(str(sample),language='es',fp16=False,verbose=None)
    return {'model':'base','device':'cpu','source':'existing_sample_mp3','download_performed':False,'live_microphone_used':False,'language':response.get('language'),'transcribed_characters':len(response.get('text','').strip()),'nonempty':bool(response.get('text','').strip()),'segments':len(response.get('segments',[]))}

if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'runtime'
    if mode=='runtime':
        for name,fn in [('syntax',syntax),('imports',imports),('config',configcheck),('cli_contract',cli),('audio_devices',audio_devices),('onnx_model',onnx),('whisper_cache',whisper_cache),('binaries',binaries),('gui',gui)]:check(name,fn)
    elif mode=='network':check('endpoints',endpoints)
    elif mode=='inference':check('generations',generations)
    elif mode=='stt':check('local_stt',local_stt)
    elif mode=='focused':
        check('binaries',binaries)
        check('gui',gui)
    REPORT.mkdir(parents=True,exist_ok=True)
    tag=f'{sys.version_info.major}{sys.version_info.minor}'
    p=REPORT/(mode+'-'+tag+'.json')
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('REPORT: '+str(p),flush=True)
