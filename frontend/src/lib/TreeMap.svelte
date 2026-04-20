<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let data = []; // Array of file objects
  export let onFileSelect;

  let svgElement;

  $: if (data.length > 0 && svgElement) {
    renderTreeMap();
  }

  function renderTreeMap() {
    const width = 800;
    const height = 500;

    const svg = d3.select(svgElement)
      .attr("viewBox", [0, 0, width, height]);

    svg.selectAll("*").remove();

    // 1. Transform flat list into hierarchy
    const root = d3.hierarchy({
      name: "root",
      children: buildHierarchy(data)
    })
    .sum(d => d.size_bytes || 100) // Fallback size
    .sort((a, b) => b.value - a.value);

    d3.treemap()
      .size([width, height])
      .padding(2)
      (root);

    const colorScale = {
      'safe': '#22c55e',    // Green
      'caution': '#eab308', // Yellow
      'restricted': '#ef4444' // Red
    };

    const nodes = svg.selectAll("g")
      .data(root.descendants().filter(d => d.depth > 0))
      .join("g")
      .attr("transform", d => `translate(${d.x0},${d.y0})`);

    nodes.append("rect")
      .attr("width", d => d.x1 - d.x0)
      .attr("height", d => d.y1 - d.y0)
      .attr("fill", d => {
        if (d.data.zone) return colorScale[d.data.zone] || '#ccc';
        return '#eee';
      })
      .attr("stroke", "#fff")
      .attr("cursor", "pointer")
      .on("click", (event, d) => {
        if (d.data.path) {
          onFileSelect(d.data);
        }
      });

    nodes.append("text")
      .attr("x", 5)
      .attr("y", 15)
      .attr("font-size", "10px")
      .attr("fill", d => (d.data.zone === 'safe' ? '#fff' : '#000'))
      .text(d => (d.x1 - d.x0 > 40 ? d.data.filename : ""));
  }

  function buildHierarchy(files) {
    const root = { name: 'root', children: [] };

    files.forEach(file => {
      const pathParts = file.path.split('/');
      let current = root;

      pathParts.forEach((part, index) => {
        let child = current.children.find(c => c.name === part);
        if (!child) {
          child = { name: part, children: [] };
          current.children.push(child);
        }
        current = child;

        if (index === pathParts.length - 1) {
          // It's the file itself
          // We add the file data to this node
          Object.assign(current, file);
          // Remove its children since it's a leaf
          current.children = [];
        }
      });
    });
    return root.children;
  }
</script>

<div class="treemap-container">
  {#if data.length === 0}
    <div class="placeholder">No data loaded. Enter a URL to begin.</div>
  {:else}
    <svg bind:this={svgElement}></svg>
  {/if}
</div>

<style>
  .treemap-container {
    width: 100%;
    height: 500px;
    background: #f3f4f6;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
  }
  .placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #6b7280;
    font-style: italic;
  }
  svg {
    display: block;
	width: 100%;
	height: 100%;
  }
</style>
