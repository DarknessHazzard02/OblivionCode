// Made by: Hazzard
// FreeCodeCamp Data Visualization - Treemap Diagram (D3): video game sales by platform
// Data: public freeCodeCamp reference dataset.
// Run it: open ../../HTML/freecodecamp/FCC_JS_Runner.html?app=Treemap_Diagram

const DATA_URL = "https://cdn.freecodecamp.org/testable-projects-fcc/data/tree_map/video-game-sales-data.json";
const W = 1000, H = 600;

const root = d3.select("#root").append("div").attr("class", "card chart");
root.append("h2").attr("id", "title").text("Video Game Sales");
root.append("p").attr("id", "description").attr("class", "muted").text("Top 100 most sold video games grouped by platform");
const tooltip = d3.select("body").append("div").attr("id", "tooltip").attr("class", "tooltip").style("opacity", 0);

d3.json(DATA_URL)
  .then((data) => {
    const hierarchy = d3.hierarchy(data).sum((d) => Number(d.value) || 0).sort((a, b) => b.value - a.value);
    d3.treemap().size([W, H]).paddingInner(1)(hierarchy);

    const categories = data.children.map((c) => c.name);
    const color = d3.scaleOrdinal()
      .domain(categories)
      .range(d3.quantize((t) => d3.interpolateRgb("#e0262e", "#3a3a44")(t), Math.max(2, categories.length)));

    const svg = root.append("svg").attr("viewBox", `0 0 ${W} ${H}`);
    const cell = svg.selectAll("g").data(hierarchy.leaves()).join("g")
      .attr("transform", (d) => `translate(${d.x0},${d.y0})`);

    cell.append("rect")
      .attr("class", "tile")
      .attr("data-name", (d) => d.data.name)
      .attr("data-category", (d) => d.data.category)
      .attr("data-value", (d) => d.data.value)
      .attr("width", (d) => d.x1 - d.x0)
      .attr("height", (d) => d.y1 - d.y0)
      .attr("fill", (d) => color(d.data.category))
      .on("mousemove", (event, d) => {
        tooltip.style("opacity", 0.95).attr("data-value", d.data.value)
          .text(`${d.data.name}\n${d.data.category}: ${d.data.value}M`)
          .style("left", event.pageX + 12 + "px").style("top", event.pageY - 30 + "px");
      })
      .on("mouseout", () => tooltip.style("opacity", 0));

    cell.append("text").attr("class", "tile-text")
      .selectAll("tspan")
      .data((d) => ((d.x1 - d.x0) > 50 ? d.data.name.split(/(?=[A-Z][^A-Z])/g) : []))
      .join("tspan")
      .attr("x", 3)
      .attr("y", (d, i) => 12 + i * 11)
      .text((d) => d);

    const legend = root.append("svg").attr("id", "legend").attr("viewBox", `0 0 ${W} 70`);
    const perRow = 9;
    const item = legend.selectAll("g").data(categories).join("g")
      .attr("transform", (d, i) => `translate(${(i % perRow) * 110},${Math.floor(i / perRow) * 22 + 5})`);
    item.append("rect").attr("class", "legend-item").attr("width", 14).attr("height", 14).attr("fill", (d) => color(d));
    item.append("text").attr("x", 20).attr("y", 12).attr("class", "legend-text").text((d) => d);
  })
  .catch((err) => root.append("p").attr("class", "error").text(`Could not load data: ${err.message}`));
