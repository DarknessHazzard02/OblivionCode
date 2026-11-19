// Made by: Hazzard
// FreeCodeCamp Data Visualization - Scatterplot Graph (D3)
// Fastest times up Alpe d'Huez, colored by doping allegations.
// Data: public freeCodeCamp reference dataset.
// Run it: open ../FCC_JS_Runner.html?app=Scatterplot_Graph

const DATA_URL = "https://raw.githubusercontent.com/freeCodeCamp/ProjectReferenceData/master/cyclist-data.json";
const W = 900, H = 500, M = { top: 40, right: 30, bottom: 40, left: 70 };
const COLORS = { clean: "#9a9aa3", doping: "#e0262e" };

const root = d3.select("#root").append("div").attr("class", "card chart");
root.append("h2").attr("id", "title").text("Doping in Professional Bicycle Racing");
const tooltip = d3.select("body").append("div").attr("id", "tooltip").attr("class", "tooltip").style("opacity", 0);

d3.json(DATA_URL)
  .then((data) => {
    data.forEach((d) => { d.time = new Date(1970, 0, 1, 0, 0, d.Seconds); });
    const svg = root.append("svg").attr("viewBox", `0 0 ${W} ${H}`);

    const x = d3.scaleLinear()
      .domain([d3.min(data, (d) => d.Year) - 1, d3.max(data, (d) => d.Year) + 1])
      .range([M.left, W - M.right]);
    const y = d3.scaleTime().domain(d3.extent(data, (d) => d.time)).nice().range([M.top, H - M.bottom]);

    svg.append("g").attr("id", "x-axis").attr("transform", `translate(0,${H - M.bottom})`)
      .call(d3.axisBottom(x).tickFormat(d3.format("d")));
    svg.append("g").attr("id", "y-axis").attr("transform", `translate(${M.left},0)`)
      .call(d3.axisLeft(y).tickFormat(d3.timeFormat("%M:%S")));
    svg.append("text").attr("class", "axis-label").attr("transform", "rotate(-90)")
      .attr("x", -H / 2).attr("y", 18).attr("text-anchor", "middle").text("Time (minutes)");

    svg.selectAll("circle").data(data).join("circle")
      .attr("class", "dot")
      .attr("cx", (d) => x(d.Year))
      .attr("cy", (d) => y(d.time))
      .attr("r", 6)
      .attr("data-xvalue", (d) => d.Year)
      .attr("data-yvalue", (d) => d.time.toISOString())
      .attr("fill", (d) => (d.Doping ? COLORS.doping : COLORS.clean))
      .on("mouseover", (event, d) => {
        tooltip.style("opacity", 0.95).attr("data-year", d.Year)
          .text(`${d.Name} (${d.Nationality})\nYear: ${d.Year}, Time: ${d.Time}${d.Doping ? "\n\n" + d.Doping : ""}`)
          .style("left", event.pageX + 12 + "px").style("top", event.pageY - 30 + "px");
      })
      .on("mouseout", () => tooltip.style("opacity", 0));

    const legend = svg.append("g").attr("id", "legend").attr("transform", `translate(${W - M.right - 230},${M.top})`);
    [["No doping allegations", COLORS.clean], ["Riders with doping allegations", COLORS.doping]]
      .forEach(([label, color], i) => {
        const row = legend.append("g").attr("transform", `translate(0,${i * 22})`);
        row.append("rect").attr("width", 14).attr("height", 14).attr("fill", color);
        row.append("text").attr("x", 20).attr("y", 12).attr("class", "legend-text").text(label);
      });
  })
  .catch((err) => root.append("p").attr("class", "error").text(`Could not load data: ${err.message}`));
