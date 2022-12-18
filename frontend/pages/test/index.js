import dynamic from 'next/dynamic';

const VectorMap = dynamic(
  // @ts-ignore
  () => import("@react-jvectormap/core").then((m) => m.VectorMap),
  { ssr: false, }
);

import rmMill from "../../Comunas/rmclMill.json";

const mapData = {
  "Padre Hurtado": 100,
  "Maipú": 200,
  "Puente Alto": 600,
  "La Florida": 300,
}

const regionStyle = {
  initial: {
    fill: "#e4e4e4",
    "fill-opacity": 0.9,
    stroke: "none",
    "stroke-width": 0,
    "stroke-opacity": 0
  },
  hover: {
    "fill": "#763452",
    "fill-opacity": 0.9,
  }
};

const containerStyle = {
  width: "inherited",
  height: "inherited",  
};

const series = {
  regions: [{
    values: mapData,
    scale: ["#e4e4e4", "#763452"],
    normalizeFunction: "polynomial"
  },]
}

export default function Home() {
  return (
    <div style={{width: "600px", height: "600px"}}>
      <VectorMap
        map={rmMill}
        backgroundColor="transparent"
        zoomOnScroll={false}
        containerStyle={containerStyle}
        containerClassName="map"
        regionStyle={regionStyle}
        series={series}
      />
    </div>
  )
}
