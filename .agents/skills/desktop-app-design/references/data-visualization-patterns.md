# Data Visualization Patterns — Charts, Dashboards, and Interactive Data

Data visualization transforms raw numbers into spatial reasoning. A well-chosen chart reveals patterns invisible in tables; a poorly chosen one obscures truth or actively misleads. This reference covers chart selection, interaction design, accessibility, dashboard composition, implementation patterns, real-time data handling, and the anti-patterns that undermine every category.

---

## 1. Chart Selection Matrix

Choosing the right chart type is the single highest-leverage decision in data visualization. The matrix below maps analytical purpose to recommended chart types, with rationale for each pairing.

### Comparison — How do values differ across categories?

| Data Shape | Recommended Chart | Rationale |
|---|---|---|
| Few categories (2-7) | Vertical bar chart | Position on a common baseline is the most accurate visual encoding for quantity comparison. |
| Many categories (8-25) | Horizontal bar chart | Horizontal layout accommodates long category labels and supports scanning top-to-bottom. |
| Two measures per category | Grouped bar chart | Side-by-side bars enable direct pairwise comparison without stacking confusion. |
| Ranked values | Sorted bar chart or lollipop chart | Sorting by value rather than alphabetical order makes the rank story immediate. Lollipop charts reduce ink-to-data ratio. |
| Part-to-whole with comparison | Stacked bar chart (100%) | Normalizing to 100% shows proportional composition and enables cross-category comparison. |
| Single KPI vs. target | Bullet chart | Stephen Few's bullet chart replaces gauges — it shows actual, target, and qualitative ranges in minimal space. |

### Composition — What makes up the whole?

| Data Shape | Recommended Chart | Rationale |
|---|---|---|
| Parts of a whole (2-5 parts) | Stacked bar chart or donut chart | Stacked bars are more accurate; donut charts work for a single high-level proportion when exact comparison is not needed. |
| Hierarchical composition | Treemap | Area encoding reveals nested proportions. Best when leaf-node count is under 50. |
| Deep hierarchies | Sunburst chart | Radial layout handles 3+ levels of nesting better than treemap for exploration. |
| Composition over time | Stacked area chart | Shows how proportional makeup shifts across a time axis. Use with caution — mid-stream categories are hard to read. |
| Simple proportion (one metric) | Single-value donut or progress bar | A single arc or bar showing "65% complete" is immediately readable. |

### Distribution — How are values spread?

| Data Shape | Recommended Chart | Rationale |
|---|---|---|
| Single variable distribution | Histogram | Bins reveal shape (normal, skewed, bimodal) that summary statistics hide. |
| Distribution comparison (2-5 groups) | Box plot or violin plot | Box plots show quartiles and outliers; violin plots add density shape for richer comparison. |
| Density estimation | Kernel density plot | Smooth curves avoid bin-width sensitivity and overlay well for group comparison. |
| Individual data points visible | Strip plot or beeswarm | Showing every point prevents the ecological fallacy of aggregation. Beeswarm avoids overlap. |
| Bivariate distribution | 2D histogram or hexbin plot | Binning prevents overplotting that scatterplots suffer at scale (>10,000 points). |

### Relationship — How do variables correlate?

| Data Shape | Recommended Chart | Rationale |
|---|---|---|
| Two continuous variables | Scatterplot | Position on two axes reveals correlation, clusters, and outliers simultaneously. |
| Three variables | Bubble chart | Third variable encoded as area. Use sparingly — area perception is less accurate than position. |
| Many-variable correlation | Correlation matrix heatmap | Color-encoded matrix shows pairwise relationships across 5-20 variables at once. |
| Network relationships | Node-link diagram or adjacency matrix | Node-link for sparse graphs (<200 nodes); adjacency matrix for dense or large graphs. |
| Categorical relationship | Parallel coordinates | Each variable is an axis; lines connecting values reveal clusters and outliers across dimensions. |

### Temporal — How do values change over time?

| Data Shape | Recommended Chart | Rationale |
|---|---|---|
| Single time series | Line chart | Connected points imply continuity and order — the correct encoding for temporal data. |
| Multiple time series (2-7) | Multi-line chart | Direct overlay enables comparison. Beyond 7 lines, use small multiples instead. |
| Many time series (8+) | Small multiples (sparklines) | Each series gets its own mini-chart. Shared axes enable comparison without spaghetti. |
| Cyclical patterns | Radial line chart or calendar heatmap | Calendar heatmaps reveal day-of-week and seasonal patterns; radial charts show hourly cycles. |
| Event-annotated time series | Line chart with annotation markers | Vertical lines or point markers contextualize spikes and drops with causal events. |
| Cumulative over time | Area chart | Filled area emphasizes accumulated quantity. Useful for revenue, user growth, inventory. |

### Geospatial — Where do patterns occur?

| Data Shape | Recommended Chart | Rationale |
|---|---|---|
| Point locations | Dot map or clustered marker map | Dots show individual locations; clustering prevents overplotting at zoom-out. |
| Regional aggregation | Choropleth map | Color-encoded regions show density or magnitude by area. Normalize per-capita to avoid population bias. |
| Flow between locations | Flow map or arc diagram | Line thickness encodes volume; direction encodes flow. |
| Density surface | Heatmap overlay | Kernel density estimation on a map reveals hotspots without discrete boundaries. |
| Proportions by region | Cartogram or proportional symbol map | Cartograms resize regions by data; proportional symbols avoid the large-area bias of choropleths. |

---

## 2. Interactive Patterns

Static charts inform; interactive charts enable exploration. Each interaction pattern below serves a distinct analytical task.

### Tooltip Design

Tooltips are the most common chart interaction. They answer "what exactly is this data point?"

- **Trigger**: Hover on desktop, tap on touch. Use a 200ms delay to prevent flicker on mousemove.
- **Content hierarchy**: Primary value (bold, larger), secondary context (category, date), optional tertiary (percentage, rank).
- **Positioning**: Prefer top-right of the cursor. Flip when near viewport edges. Never obscure the data point being inspected.
- **Formatting**: Use locale-aware number formatting. Abbreviate large numbers (1.2M, not 1,200,000). Include units.
- **Multi-series tooltips**: When multiple lines share an x-axis, show a vertical crosshair and list all series values in a single tooltip, sorted by value descending.

### Zoom and Pan

Zoom and pan enable focus on dense regions without losing global context.

- **Semantic zoom**: Change the level of detail as users zoom in — show aggregated values at zoom-out, individual data points at zoom-in. This is more valuable than geometric zoom alone.
- **Axis zoom**: Allow zooming on a single axis (e.g., zoom the x-axis time range without changing the y-axis scale). Scroll-wheel on the axis area is a natural mapping.
- **Reset control**: Always provide a visible "Reset zoom" button. Users who zoom in frequently lose their bearings.
- **Minimap**: For large datasets, show a small overview with a viewport rectangle indicating the current zoom region.

### Drill-Down

Drill-down moves from aggregate to detail, revealing the data behind a summary.

- **Visual cue**: Use a pointer cursor and subtle underline or highlight to indicate that a bar, slice, or cell is clickable.
- **Breadcrumb trail**: Show the drill path (All > Region > Country > City) so users can navigate back to any level.
- **Animation**: Animate the transition — bars splitting into sub-bars, a map zooming into a region. This preserves spatial context and reduces disorientation.
- **Data-level indicator**: Show a small indicator (e.g., a "+" icon or chevron) on aggregated elements that have children.

### Brush Selection

Brushing selects a subset of data by dragging across a range.

- **1D brush**: Drag along the x-axis to select a time range. Show the selected range with a highlighted overlay and handles for resizing.
- **2D brush**: Drag a rectangle on a scatterplot to select a cluster. Show the selected region with a semi-transparent overlay.
- **Snap behavior**: For categorical axes, snap the brush to category boundaries. For continuous axes, allow free positioning.
- **Selection count**: Display the number of selected data points and aggregate statistics (mean, sum) for the selection.

### Linked Views (Coordinated Multiple Views)

Linked views connect multiple charts so that interaction in one updates all others.

- **Highlight linking**: Hovering a category in one chart highlights the same category across all linked charts. Use consistent color encoding.
- **Filter linking**: Brushing a range in one chart filters the data shown in all linked charts. This is the most powerful exploration pattern for multivariate data.
- **Detail linking**: Clicking a data point in an overview chart updates a detail panel showing the individual record or a zoomed sub-chart.
- **Implementation**: Use a shared state store (React context, Zustand, or Observable reactive variables) to synchronize selection state across components.

### Cross-Filtering

Cross-filtering is a specific form of linked views where each chart acts as both a display and a filter control.

- **Pattern**: A dashboard has 4 charts. Clicking "Q3" on the bar chart filters the line chart, scatterplot, and table to Q3 data only. Clicking a cluster in the scatterplot further narrows all views.
- **Visual feedback**: Dim unselected data rather than removing it. This preserves context and shows what was filtered out.
- **Reset**: Provide both per-chart reset (click to clear this filter) and global reset (clear all filters). Show active filter count.

### Detail-on-Demand

Shneiderman's information-seeking mantra: "Overview first, zoom and filter, then details on demand."

- **Progressive disclosure**: Start with the highest-level summary. Let users drill, filter, and hover to reach granular data.
- **Side panel**: Clicking a data point opens a detail panel (not a modal) showing the full record, related records, and contextual actions.
- **Data table toggle**: Provide a "View as table" toggle that shows the underlying data in a sortable, searchable table. Analysts trust the raw numbers.

---

## 3. Responsive Visualization

Charts must work from 320px mobile screens to 2560px desktop monitors. This is not about shrinking — it is about strategic adaptation.

### Breakpoint Strategies

| Viewport Width | Strategy |
|---|---|
| > 1200px | Full chart with all labels, legends, annotations, and interactive features. |
| 768-1200px | Reduce legend to inline or collapsed. Abbreviate axis labels. Reduce annotation density. |
| 480-768px | Switch grouped bars to stacked. Replace multi-line charts with small multiples or a single line with a series selector. Move legend to below the chart. |
| < 480px | Use sparklines or single-KPI cards. Replace charts with summary statistics where the visual encoding adds no value at this size. Consider horizontal scrolling for time series. |

### Simplification at Small Sizes

- **Reduce data points**: Downsample a 365-day line chart to weekly or monthly at small breakpoints. Use LTTB (Largest Triangle Three Buckets) algorithm for perceptually faithful downsampling.
- **Remove gridlines**: At small sizes, gridlines create noise. Keep only the baseline and perhaps one reference line.
- **Rotate or truncate labels**: Below 600px, rotate x-axis labels to 45 degrees. Below 400px, show every other label or abbreviate (Jan, Feb, Mar).
- **Collapse legends**: Replace a color legend with direct labels on the lines or bars themselves. Below 400px, use a dropdown selector to toggle series visibility.
- **Touch targets**: Increase interactive target areas to at least 44x44px for touch. This may require spacing out bars or points.

### Data Reduction Techniques

- **Aggregation**: Roll up daily data to weekly or monthly. Group long-tail categories into "Other."
- **Filtering**: Show only the top N categories. Provide a control to adjust N.
- **Sampling**: For scatterplots with millions of points, use reservoir sampling to display a representative subset.
- **Level of detail**: At zoom-out, show county-level data. At zoom-in, show city-level. This mirrors semantic zoom.

---

## 4. Accessible Charts

Charts are among the least accessible UI components. Making them usable for everyone requires deliberate engineering.

### Keyboard Navigation for Data Points

- **Tab to chart**: The chart container should be a single tab stop. Pressing Enter or Space enters the chart.
- **Arrow keys within chart**: Left/Right moves between data points (or categories). Up/Down moves between series. Announce the current value via a live region.
- **Escape exits**: Pressing Escape returns focus to the chart container.
- **Home/End**: Jump to the first or last data point.

```html
<div role="img" aria-label="Bar chart showing quarterly revenue for 2025"
     tabindex="0" aria-roledescription="interactive chart">
  <svg role="group" aria-label="Data series: Revenue">
    <rect role="graphics-symbol" aria-roledescription="bar"
          aria-label="Q1 2025: $4.2 million" tabindex="-1" />
    <rect role="graphics-symbol" aria-roledescription="bar"
          aria-label="Q2 2025: $5.1 million" tabindex="-1" />
  </svg>
</div>
```

### ARIA Roles for SVG Charts

- **Container**: `role="img"` with a descriptive `aria-label` summarizing the chart type, data subject, and time range.
- **`aria-roledescription`**: Use `"interactive chart"`, `"bar"`, `"data point"`, `"line"` to provide semantic context that generic roles cannot.
- **Groups**: Wrap each data series in `<g role="group" aria-label="Series: Revenue">`.
- **Live regions**: When users navigate data points, update an `aria-live="polite"` region with the current value: "Q3, Revenue, 6.8 million dollars."

### Sonification

Sonification maps data values to audio pitch, enabling non-visual data exploration.

- **Pitch mapping**: Higher values produce higher pitch. Use a pentatonic scale to avoid dissonance.
- **Temporal mapping**: Play time-series data as a sequence of tones. Allow speed control (0.5x to 4x).
- **Stereo panning**: For geospatial or categorical data, pan left-to-right to indicate position.
- **Libraries**: Tone.js provides Web Audio synthesis. Highcharts includes built-in sonification. Observable Plot can be extended with custom audio output.

### Alt Text Patterns

Every chart needs alt text. The pattern depends on the chart's purpose.

- **Decorative chart** (used as visual embellishment): `alt=""` — skip it.
- **Informational chart**: Describe the conclusion: "Bar chart showing revenue grew 23% from Q1 to Q4 2025, with Q3 as the peak quarter at $6.8M."
- **Exploratory chart**: Describe the structure: "Scatterplot of 500 customer records plotting satisfaction score against response time. A negative correlation is visible. Interactive: use arrow keys to explore individual points."
- **Length**: Keep alt text under 150 characters for simple charts. For complex charts, use `aria-describedby` pointing to a longer description or data table.

### Color-Blind Safe Palettes

Approximately 8% of males and 0.5% of females have color vision deficiency. Never rely on color alone.

- **Recommended palettes**: Use ColorBrewer qualitative palettes (Set2, Dark2) or the Okabe-Ito palette, which were designed for color-blind safety.
- **Redundant encoding**: Combine color with shape (circles vs. squares), pattern (solid vs. dashed lines), or direct labels.
- **Simulation testing**: Use tools like Coblis or the Chrome DevTools "Emulate vision deficiencies" feature to test protanopia, deuteranopia, and tritanopia rendering.
- **Maximum hues**: Limit categorical color palettes to 6-8 distinct hues. Beyond that, no palette is reliably distinguishable.

### High-Contrast Mode

- **Detect `prefers-contrast: more`**: Increase stroke widths from 1px to 2px, use black/white backgrounds, and increase font weight.
- **Detect `forced-colors: active`**: In Windows High Contrast Mode, all colors are overridden by the system. Ensure chart elements use `currentColor` or system color keywords (`CanvasText`, `LinkText`).
- **Minimum contrast**: Data-encoding colors must have at least 3:1 contrast against their background (WCAG 1.4.11 non-text contrast).

---

## 5. Dashboard Composition

A dashboard is not a collection of charts — it is a narrative about data, structured for a specific audience and decision context.

### Layout Grids

- **12-column grid**: Use a 12-column grid with 16-24px gutters. Charts span 4, 6, 8, or 12 columns depending on importance.
- **Vertical rhythm**: Maintain consistent card heights within each row. Use aspect ratios (16:9 for wide charts, 4:3 for square) rather than fixed pixel heights.
- **Z-pattern reading**: Place the most important KPI or chart in the top-left. Secondary metrics flow right and down.
- **Breakpoint collapse**: At tablet width, 4-column cards become 6-column (two per row). At mobile, all cards become 12-column (full width, stacked).

### Card-Based Metrics

Each dashboard card is a self-contained unit with consistent structure.

- **Card anatomy**: Title (what is measured), primary metric (the number), trend indicator (up/down arrow with percentage), sparkline or mini-chart, time range label.
- **Card sizes**: Small (KPI only, no chart), Medium (KPI + sparkline), Large (full interactive chart).
- **Card states**: Loading (skeleton), Error (retry button), Empty (explanatory text), Populated (normal).
- **Card actions**: Expand to full screen, export data, share link, configure time range.

### KPI Hierarchy

- **Level 1 (Hero KPIs)**: 1-3 metrics that answer "is the business healthy?" Displayed largest, at the top of the dashboard. Example: Total Revenue, Active Users, NPS.
- **Level 2 (Supporting KPIs)**: 4-8 metrics that explain why L1 metrics are moving. Displayed as medium cards in a row below the hero. Example: Revenue by channel, Churn rate, Feature adoption.
- **Level 3 (Diagnostic charts)**: Full charts that enable investigation. Displayed as large cards occupying full rows. Example: Revenue over time with annotations, Funnel conversion by step, Cohort retention matrix.

### Sparklines

Sparklines are word-sized charts that show trend without detail.

- **Implementation**: A sparkline is a line chart with no axes, no labels, no gridlines. Just the line itself, typically 80-150px wide and 20-30px tall.
- **Context markers**: Show the first value, last value, min, and max as small dots. This gives the sparkline anchoring context.
- **Color encoding**: Use a single color for the line. Use red/green (with icon redundancy) only if the sparkline represents a metric where direction is inherently good or bad.

### Data Density vs. Clarity

Edward Tufte advocates maximizing the data-ink ratio. But dashboards serve busy people who glance, not study.

- **High density is appropriate for**: Analysts who use the dashboard daily, monitoring screens that show many metrics simultaneously, printed reports.
- **Low density is appropriate for**: Executive summaries, first-time viewers, mobile screens, public-facing dashboards.
- **Balance technique**: Start with high density, then remove elements one at a time. Stop removing when the next removal would cause a user to misinterpret the data or miss a pattern.
- **White space is data**: Generous padding between cards is not wasted space — it creates visual grouping and reduces cognitive load.

---

## 6. Chart Component Patterns

The following React components use D3 for scales and Observable Plot conventions. Each includes accessibility attributes.

### Accessible Bar Chart

```tsx
import * as d3 from "d3";
import { useRef, useEffect, useState } from "react";

interface BarDatum {
  category: string;
  value: number;
}

interface BarChartProps {
  data: BarDatum[];
  width?: number;
  height?: number;
  ariaLabel: string;
}

export function BarChart({
  data,
  width = 600,
  height = 400,
  ariaLabel,
}: BarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [focusIndex, setFocusIndex] = useState(-1);
  const margin = { top: 20, right: 20, bottom: 40, left: 60 };

  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const xScale = d3
    .scaleBand()
    .domain(data.map((d) => d.category))
    .range([0, innerWidth])
    .padding(0.2);

  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.value) ?? 0])
    .nice()
    .range([innerHeight, 0]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight") {
      setFocusIndex((prev) => Math.min(prev + 1, data.length - 1));
    } else if (e.key === "ArrowLeft") {
      setFocusIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Home") {
      setFocusIndex(0);
    } else if (e.key === "End") {
      setFocusIndex(data.length - 1);
    } else if (e.key === "Escape") {
      setFocusIndex(-1);
      svgRef.current?.focus();
    }
  };

  return (
    <>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        role="img"
        aria-label={ariaLabel}
        aria-roledescription="interactive bar chart"
        tabIndex={0}
        onKeyDown={handleKeyDown}
      >
        <g transform={`translate(${margin.left},${margin.top})`}>
          {data.map((d, i) => (
            <rect
              key={d.category}
              x={xScale(d.category)}
              y={yScale(d.value)}
              width={xScale.bandwidth()}
              height={innerHeight - yScale(d.value)}
              fill={i === focusIndex ? "#1a73e8" : "#4285f4"}
              stroke={i === focusIndex ? "#000" : "none"}
              strokeWidth={i === focusIndex ? 2 : 0}
              role="graphics-symbol"
              aria-roledescription="bar"
              aria-label={`${d.category}: ${d.value.toLocaleString()}`}
              tabIndex={-1}
            />
          ))}
          {/* X Axis */}
          <g transform={`translate(0,${innerHeight})`}>
            {data.map((d) => (
              <text
                key={d.category}
                x={(xScale(d.category) ?? 0) + xScale.bandwidth() / 2}
                y={24}
                textAnchor="middle"
                fontSize={12}
                aria-hidden="true"
              >
                {d.category}
              </text>
            ))}
          </g>
        </g>
      </svg>
      {/* Live region for screen reader announcements */}
      <div aria-live="polite" className="sr-only">
        {focusIndex >= 0 &&
          `${data[focusIndex].category}: ${data[focusIndex].value.toLocaleString()}`}
      </div>
    </>
  );
}
```

### Accessible Line Chart

```tsx
import * as d3 from "d3";
import { useRef, useState } from "react";

interface LineDatum {
  date: Date;
  value: number;
}

interface LineChartProps {
  data: LineDatum[];
  width?: number;
  height?: number;
  ariaLabel: string;
}

export function LineChart({
  data,
  width = 600,
  height = 400,
  ariaLabel,
}: LineChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [focusIndex, setFocusIndex] = useState(-1);
  const margin = { top: 20, right: 20, bottom: 40, left: 60 };

  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const xScale = d3
    .scaleTime()
    .domain(d3.extent(data, (d) => d.date) as [Date, Date])
    .range([0, innerWidth]);

  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.value) ?? 0])
    .nice()
    .range([innerHeight, 0]);

  const line = d3
    .line<LineDatum>()
    .x((d) => xScale(d.date))
    .y((d) => yScale(d.value))
    .curve(d3.curveMonotoneX);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight") {
      setFocusIndex((p) => Math.min(p + 1, data.length - 1));
    } else if (e.key === "ArrowLeft") {
      setFocusIndex((p) => Math.max(p - 1, 0));
    } else if (e.key === "Home") {
      setFocusIndex(0);
    } else if (e.key === "End") {
      setFocusIndex(data.length - 1);
    } else if (e.key === "Escape") {
      setFocusIndex(-1);
      svgRef.current?.focus();
    }
  };

  const formatDate = d3.timeFormat("%b %d, %Y");

  return (
    <>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        role="img"
        aria-label={ariaLabel}
        aria-roledescription="interactive line chart"
        tabIndex={0}
        onKeyDown={handleKeyDown}
      >
        <g transform={`translate(${margin.left},${margin.top})`}>
          <path
            d={line(data) ?? ""}
            fill="none"
            stroke="#4285f4"
            strokeWidth={2}
            aria-hidden="true"
          />
          {data.map((d, i) => (
            <circle
              key={i}
              cx={xScale(d.date)}
              cy={yScale(d.value)}
              r={i === focusIndex ? 6 : 3}
              fill={i === focusIndex ? "#1a73e8" : "#4285f4"}
              stroke={i === focusIndex ? "#000" : "none"}
              strokeWidth={i === focusIndex ? 2 : 0}
              role="graphics-symbol"
              aria-roledescription="data point"
              aria-label={`${formatDate(d.date)}: ${d.value.toLocaleString()}`}
              tabIndex={-1}
            />
          ))}
        </g>
      </svg>
      <div aria-live="polite" className="sr-only">
        {focusIndex >= 0 &&
          `${formatDate(data[focusIndex].date)}: ${data[focusIndex].value.toLocaleString()}`}
      </div>
    </>
  );
}
```

### Accessible Scatterplot

```tsx
import * as d3 from "d3";
import { useRef, useState } from "react";

interface ScatterDatum {
  x: number;
  y: number;
  label: string;
  category: string;
}

interface ScatterPlotProps {
  data: ScatterDatum[];
  xLabel: string;
  yLabel: string;
  width?: number;
  height?: number;
  ariaLabel: string;
}

export function ScatterPlot({
  data,
  xLabel,
  yLabel,
  width = 600,
  height = 400,
  ariaLabel,
}: ScatterPlotProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [focusIndex, setFocusIndex] = useState(-1);
  const margin = { top: 20, right: 20, bottom: 50, left: 60 };

  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const xScale = d3
    .scaleLinear()
    .domain(d3.extent(data, (d) => d.x) as [number, number])
    .nice()
    .range([0, innerWidth]);

  const yScale = d3
    .scaleLinear()
    .domain(d3.extent(data, (d) => d.y) as [number, number])
    .nice()
    .range([innerHeight, 0]);

  const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

  // Sort data for consistent keyboard navigation (left to right)
  const sorted = [...data].sort((a, b) => a.x - b.x);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight") {
      setFocusIndex((p) => Math.min(p + 1, sorted.length - 1));
    } else if (e.key === "ArrowLeft") {
      setFocusIndex((p) => Math.max(p - 1, 0));
    } else if (e.key === "Home") {
      setFocusIndex(0);
    } else if (e.key === "End") {
      setFocusIndex(sorted.length - 1);
    } else if (e.key === "Escape") {
      setFocusIndex(-1);
      svgRef.current?.focus();
    }
  };

  return (
    <>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        role="img"
        aria-label={ariaLabel}
        aria-roledescription="interactive scatter plot"
        tabIndex={0}
        onKeyDown={handleKeyDown}
      >
        <g transform={`translate(${margin.left},${margin.top})`}>
          {sorted.map((d, i) => (
            <circle
              key={d.label}
              cx={xScale(d.x)}
              cy={yScale(d.y)}
              r={i === focusIndex ? 8 : 5}
              fill={colorScale(d.category)}
              stroke={i === focusIndex ? "#000" : "none"}
              strokeWidth={i === focusIndex ? 2 : 0}
              opacity={0.8}
              role="graphics-symbol"
              aria-roledescription="data point"
              aria-label={`${d.label}: ${xLabel} ${d.x}, ${yLabel} ${d.y}, category ${d.category}`}
              tabIndex={-1}
            />
          ))}
          {/* Axis labels */}
          <text
            x={innerWidth / 2}
            y={innerHeight + 40}
            textAnchor="middle"
            fontSize={13}
            aria-hidden="true"
          >
            {xLabel}
          </text>
          <text
            transform={`rotate(-90)`}
            x={-innerHeight / 2}
            y={-45}
            textAnchor="middle"
            fontSize={13}
            aria-hidden="true"
          >
            {yLabel}
          </text>
        </g>
      </svg>
      <div aria-live="polite" className="sr-only">
        {focusIndex >= 0 &&
          `${sorted[focusIndex].label}: ${xLabel} ${sorted[focusIndex].x}, ${yLabel} ${sorted[focusIndex].y}, category ${sorted[focusIndex].category}`}
      </div>
    </>
  );
}
```

---

## 7. Real-Time Data Visualization

Real-time data introduces temporal challenges that static charts do not face: data arrives continuously, values change unpredictably, and the display must update without disorienting the user.

### Streaming Updates

- **WebSocket or SSE**: Use WebSocket for bidirectional communication (e.g., user can request historical data). Use Server-Sent Events for one-way server-to-client data push. SSE is simpler and auto-reconnects.
- **Buffer and batch**: Do not re-render on every incoming data point. Buffer incoming data and flush to the chart at a fixed interval (e.g., every 500ms or 1 second). This prevents excessive re-renders and keeps frame rate stable.
- **Sliding window**: For time-series displays, maintain a fixed window (e.g., last 5 minutes). As new data enters on the right, old data exits on the left. The axis shifts smoothly.
- **Append-only rendering**: For line charts, compute only the new path segment rather than recomputing the entire path. Use `requestAnimationFrame` to schedule updates.

### Animation for Data Changes

Animation in data visualization serves a functional purpose: it helps users track which elements moved and where.

- **Transition duration**: 300-500ms for value updates. Shorter than UI animation because data updates are frequent.
- **Easing**: Use `ease-out` for elements entering (they arrive fast, settle slowly). Use `ease-in-out` for elements moving (smooth acceleration and deceleration).
- **Enter/Exit**: New data points fade in (opacity 0 to 1). Exiting data points fade out (opacity 1 to 0). Do not use movement for enter/exit — it implies the data moved rather than appeared/disappeared.
- **Value changes**: Bars grow or shrink smoothly. Numbers count up or down (use a counter animation). Line chart points interpolate to new positions.
- **Avoid gratuitous animation**: If the chart updates every second, do not animate every update. Show the latest state instantly and reserve animation for significant changes (threshold crossings, anomalies).

### Optimistic Rendering

In dashboards connected to user actions (e.g., a sales team dashboard), render expected changes immediately.

- **Pattern**: When a user marks a deal as "closed," update the revenue chart immediately while the server request is in-flight. If the server rejects, roll back with a subtle flash to indicate the correction.
- **Confidence indicators**: For predictive dashboards, show the predicted value with a dashed line or confidence interval band, and the actual confirmed value with a solid line.
- **Stale data indicator**: If the data connection drops, show a timestamp ("Last updated: 2 minutes ago") and a visual indicator (dimmed chart, warning icon) so users know the data may be stale.

---

## 8. Anti-Patterns

These are visualization choices that mislead, confuse, or waste the viewer's cognitive effort. Avoid them.

### Pie Charts for More Than 5 Segments

Humans are poor at comparing angles and areas. With more than 5 slices, pie charts become unreadable. At 8+ slices, they are decorative noise. Use a horizontal bar chart sorted by value instead. The only acceptable use of a pie chart is showing one dominant proportion ("78% of users are on mobile") where the visual gestalt of "most of the circle" is the message.

### 3D Charts

Adding a third spatial dimension to 2D data distorts perception. Bars in the back of a 3D bar chart appear shorter than bars in the front, even when their values are identical. 3D pie charts tilt the perspective so that slices closer to the viewer appear larger. There is no data type that is better served by a 3D chart than its 2D equivalent. If you have three variables, use a bubble chart, parallel coordinates, or small multiples — not 3D.

### Dual-Axis Confusion

Dual y-axis charts (one series on the left axis, another on the right axis) are dangerous because the two scales are independent. By adjusting the range of either axis, you can make any two trends appear correlated, anti-correlated, or unrelated. If you must compare two metrics with different units, use two vertically stacked charts sharing the same x-axis. If a dual-axis chart is truly unavoidable, clearly label each axis with color-matched text and provide an explicit explanation of what the chart shows.

### Rainbow Color Scales

Rainbow (ROYGBIV) color scales are perceptually non-uniform. The yellow band appears brighter and draws disproportionate attention, creating false boundaries in continuous data. Green-to-cyan transitions are nearly invisible, hiding real variation. Use perceptually uniform sequential scales (Viridis, Inferno, Plasma, Cividis) for continuous data. Use diverging scales (RdBu, PiYG) for data with a meaningful midpoint. Reserve categorical palettes for categorical data.

### Truncated Y-Axis

Starting the y-axis at a value other than zero exaggerates small differences. A bar chart showing values from 98 to 102 with a baseline of 97 makes a 4% range look like a 400% range. For bar charts, always start at zero — the length of the bar is the visual encoding, and a non-zero baseline breaks that encoding. For line charts, a non-zero baseline is acceptable when the purpose is to show trend rather than magnitude, but label the axis clearly and consider adding a note.

### Chart Junk

Decorative elements — gradients, shadows, background images, icons inside bars, excessive gridlines — reduce the signal-to-noise ratio. Every pixel that does not encode data or aid interpretation is chart junk. This does not mean charts should be ugly — clean typography, thoughtful spacing, and intentional color are aesthetic choices that aid comprehension. The test is: "If I remove this element, does the viewer lose any information?" If the answer is no, remove it.

### Misleading Aggregation

Showing only averages hides distribution. A bar chart showing "average response time: 200ms" conceals the fact that 95th percentile is 2,000ms. Always consider what summary statistic serves the analytical question. Show distributions (histograms, box plots) when the spread matters. Show confidence intervals or error bars when uncertainty matters. Annotate with sample sizes when magnitudes differ.

### Animation as Decoration

Animated chart entrances (bars growing from zero, lines drawing left to right) are acceptable on first load but should not repeat on every data update. Gratuitous animation delays comprehension — the viewer must wait for the animation to complete before reading the data. If a dashboard refreshes every 30 seconds, the entrance animation runs 120 times per hour, wasting minutes of cumulative attention. Reserve animation for transitions that convey information: an element moving because its rank changed, a threshold line appearing because a limit was exceeded.

---

## Summary Checklist

Before shipping any data visualization:

1. Does the chart type match the analytical question?
2. Can a user with no context understand the main takeaway within 5 seconds?
3. Is the chart keyboard-navigable with screen reader announcements?
4. Does the color palette work for color-blind users and in high-contrast mode?
5. Does the chart adapt meaningfully (not just shrink) at smaller viewports?
6. Are tooltips, drill-down, and detail-on-demand available for exploration?
7. Is the y-axis baseline appropriate (zero for bars, contextual for lines)?
8. Have you avoided every anti-pattern listed in section 8?

If the answer to all eight is yes, ship it.
