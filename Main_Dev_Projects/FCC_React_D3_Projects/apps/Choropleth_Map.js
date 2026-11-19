// Made by: Hazzard
// FreeCodeCamp Data Visualization - Choropleth Map (D3 + topojson)
// US counties colored by % of adults with a bachelor's degree or higher.
// Data: public freeCodeCamp reference datasets.
// Run it: open ../FCC_JS_Runner.html?app=Choropleth_Map

const BASE = "https://cdn.freecodecamp.org/testable-projects-fcc/data/choropleth_map/";
const COUNTY_URL = BASE + "counties.json";
const EDU_URL = BASE + "for_user_education.json";
const W = 960, H = 640;

const root = d3.select("#root").append("div").attr("class", "card chart");
root.append("h2").attr("id", "title").text("United States Educational Attainment");
root.append("p").attr("id", "description").attr("class", "muted")
  .text("Adults 25+ with a bachelor's degree or higher (2010-2014)");
const tooltip = d3.select("body").append("div").attr("id", "tooltip").attr("class", "tooltip").style("opacity", 0);

Promise.all([d3.json(COUNTY_URL), d3.json(EDU_URL)])
  .then(([us, education]) => {
    const byFips = new Map(education.map((d) => [d.fips, d]));
    const color = d3.scaleThreshold()
      .domain([10, 20, 30, 40, 50, 60])
      .range(["#2b2b33", "#4a2a30", "#6e2a2e", "#93282c", "#b8262b", "#e0262e", "#ff7a7e"]);

    const svg = root.append("svg").attr("viewBox", `0 0 ${W} ${H}`);
    const path = d3.geoPath();   // the dataset is already projected

    svg.append("g").selectAll("path")
      .data(topojson.feature(us, us.objects.counties).features)
      .join("path")
      .attr("class", "county")
      .attr("d", path)
      .attr("data-fips", (d) => d.id)
      .attr("data-education", (d) => (byFips.get(d.id) ? byFips.get(d.id).bachelorsOrHigher : 0))
      .attr("fill", (d) => (byFips.get(d.id) ? color(byFips.get(d.id).bachelorsOrHigher) : "#555"))
      .on("mouseover", (event, d) => {
        const row = byFips.get(d.id);
        tooltip.style("opacity", 0.95).attr("data-education", row ? row.bachelorsOrHigher : 0)
          .text(row ? `${row.area_name}, ${row.state}: ${row.bachelorsOrHigher}%` : "No data")
          .style("left", event.pageX + 12 + "px").style("top", event.pageY - 30 + "px");
      })
      .on("mouseout", () => tooltip.style("opacity", 0));

    svg.append("path")
      .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
      .attr("class", "state-border")
      .attr("d", path);

    const legendX = d3.scaleLinear().domain([0, 70]).range([0, 280]);
    const legend = svg.append("g").attr("id", "legend").attr("transform", `translate(${W - 330},30)`);
    legend.selectAll("rect")
      .data(color.range().map((c) => {
        const [lo, hi] = color.invertExtent(c);
        return [lo === undefined ? 0 : lo, hi === undefined ? 70 : hi, c];
      }))
      .join("rect")
      .attr("x", (d) => legendX(d[0]))
      .attr("width", (d) => legendX(d[1]) - legendX(d[0]))
      .attr("height", 10)
      .attr("fill", (d) => d[2]);
    legend.append("g").attr("transform", "translate(0,10)")
      .call(d3.axisBottom(legendX).tickValues(color.domain()).tickFormat((v) => v + "%"));
  })
  .catch((err) => root.append("p").attr("class", "error").text(`Could not load data: ${err.message}`));
