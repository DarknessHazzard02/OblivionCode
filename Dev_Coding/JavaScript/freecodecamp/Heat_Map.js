// Made by: Hazzard
// FreeCodeCamp Data Visualization - Heat Map (D3): monthly global land temperature
// Data: public freeCodeCamp reference dataset.
// Run it: open ../../HTML/freecodecamp/FCC_JS_Runner.html?app=Heat_Map

const DATA_URL = "https://raw.githubusercontent.com/freeCodeCamp/ProjectReferenceData/master/global-temperature.json";
const W = 1000, H = 480, M = { top: 30, right: 20, bottom: 90, left: 90 };
const MONTHS = d3.range(12).map((m) => d3.timeFormat("%B")(new Date(2000, m, 1)));

const root = d3.select("#root").append("div").attr("class", "card chart");
root.append("h2").attr("id", "title").text("Monthly Global Land-Surface Temperature");
const description = root.append("p").attr("id", "description").attr("class", "muted");
const tooltip = d3.select("body").append("div").attr("id", "tooltip").attr("class", "tooltip").style("opacity", 0);

d3.json(DATA_URL)
  .then(({ baseTemperature, monthlyVariance }) => {
    const years = d3.extent(monthlyVariance, (d) => d.year);
    description.text(`${years[0]} - ${years[1]}: base temperature ${baseTemperature}°C`);
    const temps = monthlyVariance.map((d) => baseTemperature + d.variance);
    const svg = root.append("svg").attr("viewBox", `0 0 ${W} ${H}`);

    const x = d3.scaleBand().domain(d3.range(years[0], years[1] + 1)).range([M.left, W - M.right]);
    const y = d3.scaleBand().domain(d3.range(12)).range([M.top, H - M.bottom]);
    const color = d3.scaleQuantize().domain(d3.extent(temps))
      .range(["#2b2b33", "#4a2a30", "#6e2a2e", "#93282c", "#b8262b", "#e0262e", "#ff5a5f", "#ff9a9d"]);

    svg.append("g").attr("id", "x-axis").attr("transform", `translate(0,${H - M.bottom})`)
      .call(d3.axisBottom(x).tickValues(x.domain().filter((yr) => yr % 10 === 0)));
    svg.append("g").attr("id", "y-axis").attr("transform", `translate(${M.left},0)`)
      .call(d3.axisLeft(y).tickFormat((m) => MONTHS[m]));

    svg.selectAll("rect.cell").data(monthlyVariance).join("rect")
      .attr("class", "cell")
      .attr("data-month", (d) => d.month - 1)
      .attr("data-year", (d) => d.year)
      .attr("data-temp", (d) => baseTemperature + d.variance)
      .attr("x", (d) => x(d.year))
      .attr("y", (d) => y(d.month - 1))
      .attr("width", x.bandwidth())
      .attr("height", y.bandwidth())
      .attr("fill", (d) => color(baseTemperature + d.variance))
      .on("mouseover", (event, d) => {
        const t = baseTemperature + d.variance;
        tooltip.style("opacity", 0.95).attr("data-year", d.year)
          .text(`${d.year} - ${MONTHS[d.month - 1]}\n${t.toFixed(1)}°C\n${d.variance >= 0 ? "+" : ""}${d.variance.toFixed(1)}°C`)
          .style("left", event.pageX + 12 + "px").style("top", event.pageY - 40 + "px");
      })
      .on("mouseout", () => tooltip.style("opacity", 0));

    // Legend: one swatch per color bucket
    const buckets = color.range();
    const legendScale = d3.scaleLinear().domain(color.domain()).range([0, 320]);
    const legend = svg.append("g").attr("id", "legend").attr("transform", `translate(${M.left},${H - 45})`);
    legend.selectAll("rect").data(buckets).join("rect")
      .attr("x", (c) => legendScale(color.invertExtent(c)[0]))
      .attr("width", (c) => legendScale(color.invertExtent(c)[1]) - legendScale(color.invertExtent(c)[0]))
      .attr("height", 16)
      .attr("fill", (c) => c);
    legend.append("g").attr("transform", "translate(0,16)")
      .call(d3.axisBottom(legendScale).ticks(8).tickFormat(d3.format(".1f")));
  })
  .catch((err) => root.append("p").attr("class", "error").text(`Could not load data: ${err.message}`));
