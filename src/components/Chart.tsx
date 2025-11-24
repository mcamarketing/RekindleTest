import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { motion } from "framer-motion";

interface ChartData {
  name: string;
  value: number;
}

interface ChartProps {
  data: ChartData[];
  title: string;
}

export function Chart({ data, title }: ChartProps) {
  return (
    <motion.div
      className="bg-white border border-[#e3e8ee] rounded-lg p-6 hover:shadow-md transition-shadow duration-200"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <h3 className="text-lg font-medium text-[#0a2540] mb-4">{title}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="name" tick={{ fill: "#727f96" }} />
            <YAxis tick={{ fill: "#727f96" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0a2540",
                borderColor: "#0a2540",
                color: "#ffffff",
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#8884d8"
              fillOpacity={1}
              fill="url(#colorValue)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
