// Made by: Hazzard
// FreeCodeCamp Data Visualization - Bar Chart (D3): US GDP by quarter
// Data: public freeCodeCamp reference dataset.
// Run it: open ../FCC_JS_Runner.html?app=Bar_Chart

const DATA_URL = "https://raw.githubusercontent.com/freeCodeCamp/ProjectReferenceData/master/GDP-data.json";
const W = 900, H = 460, M = { top: 40, right: 20, bottom: 40, left: 70 };

const root = d3.select("#root").append("div").attr("class", "card chart");
root.append("h2").attr("id", "title").text("United States GDP");
const tooltip = d3.select("body").append("div").attr("id", "tooltip").attr("class", "tooltip").style("opacity", 0);

d3.json(DATA_URL)
  .then(({ data }) => {
    const dates = data.map((d) => new Date(d[0]));
    const svg = root.append("svg").attr("viewBox", `0 0 ${W} ${H}`);

    const x = d3.scaleTime().domain(d3.extent(dates)).range([M.left, W - M.right]);
    const y = d3.scaleLinear().domain([0, d3.max(data, (d) => d[1])]).nice().range([H - M.bottom, M.top]);
    const barW = (W - M.left - M.right) / data.length;

    svg.append("g").attr("id", "x-axis").attr("transform", `translate(0,${H - M.bottom})`).call(d3.axisBottom(x));
    svg.append("g").attr("id", "y-axis").attr("transform", `translate(${M.left},0)`).call(d3.axisLeft(y));
    svg.append("text").attr("class", "axis-label").attr("transform", "rotate(-90)")
      .attr("x", -H / 2).attr("y", 18).attr("text-anchor", "middle").text("GDP (billions USD)");

    svg.selectAll("rect").data(data).join("rect")
      .attr("class", "bar")
      .attr("data-date", (d) => d[0])
      .attr("data-gdp", (d) => d[1])
      .attr("x", (d, i) => x(dates[i]))
      .attr("y", (d) => y(d[1]))
      .attr("width", Math.max(1, barW))
      .attr("height", (d) => H - M.bottom - y(d[1]))
      .on("mouseover", (event, d) => {
        tooltip.style("opacity", 0.95).attr("data-date", d[0])
          .text(`${d[0]}\n$${d3.format(",.1f")(d[1])} Billion`)
          .style("left", event.pageX + 12 + "px").style("top", event.pageY - 30 + "px");
      })
      .on("mouseout", () => tooltip.style("opacity", 0));
  })
  .catch((err) => root.append("p").attr("class", "error").text(`Could not load data: ${err.message}`));
