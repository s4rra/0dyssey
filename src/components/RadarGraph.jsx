import React, { lazy, Suspense } from "react";
import RadarChart from "./RadarChart";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Loader } from "lucide-react";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const Radar = lazy(() =>
  import("react-chartjs-2").then(m => ({ default: m.Radar }))
);

const Loading = () => (
  <div className="loading-fallback">
    <Loader className="spin" /> <p>Loading chart…</p>
  </div>
);

const RadarChart = ({ tagInsights }) => {
  if (!tagInsights?.length) return <p>No insights to show.</p>;

  const radarData = {
    labels: tagInsights.map(t => t.tag),
    datasets: [{
      label: "Progress",
      data: tagInsights.map(t => t.percentage),
      backgroundColor: "rgba(34,197,94,0.2)",
      borderColor: "rgba(34,197,94,1)",
      borderWidth: 2,
    }],
  };

  const radarOptions = {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: { stepSize: 20, backdropColor: "transparent" }
      }
    },
    plugins: { legend: { display: false } }
  };

  return (
    <Suspense fallback={<Loading />}>
      <Radar data={radarData} options={radarOptions} />
    </Suspense>
  );
};

export default RadarChart;
