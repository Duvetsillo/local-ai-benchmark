import psutil
import platform
import subprocess

class HardwareProfiler:
    """
    Clase encargada de detectar la arquitectura del sistema y los recursos disponibles.
    """
    def __get_cpu_info(self):
        return {
            "model": platform.processor(),
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "freq": psutil.cpu_freq().max if psutil.cpu_freq() else "N/A"
        }

    def __get_ram_info(self):
        ram = psutil.virtual_memory()
        return {
            "total": ram.total // (1024**3), # GB
            "available": ram.available // (1024**3), # GB
            "used": ram.used // (1024**3) # GB
        }

    def get_profile(self):
        return {
            "cpu": self.__get_cpu_info(),
            "ram": self.__get_ram_info(),
            "os": platform.system(),
            "arch": platform.machine()
        }

if __name__ == "__main__":
    profiler = HardwareProfiler()
    print(profiler.get_profile())
