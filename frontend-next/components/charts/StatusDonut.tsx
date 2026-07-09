"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { useTheme } from "@/lib/theme";

interface StatusDonutProps {
  compliant: number;
  partial: number;
  nonCompliant: number;
  notFound: number;
}

export function StatusDonut({
  compliant,
  partial,
  nonCompliant,
  notFound,
}: StatusDonutProps) {
  const { theme } = useTheme();

  const data = [
    { name: "Compliant", value: compliant },
    { name: "Partial", value: partial },
    { name: "Non-Compliant", value: nonCompliant },
    { name: "Not Found", value: notFound },
  ].filter((d) => d.value > 0);

  // Use theme-aware colors via CSS variables
  const COLORS: Record<string, string> = {
    Compliant: "hsl(142, 76%, 36%)",     // green-600
    Partial: "hsl(38, 92%, 50%)",         // amber-500
    "Non-Compliant": "hsl(0, 84%, 60%)",  // red-600
    "Not Found": "hsl(220, 9%, 46%)",     // gray-500
  };

  const DARK_COLORS: Record<string, string> = {
    Compliant: "hsl(142, 71%, 45%)",     // green-500
    Partial: "hsl(38, 92%, 50%)",         // amber-500
    "Non-Compliant": "hsl(0, 72%, 51%)",  // red-500
    "Not Found": "hsl(220, 9%, 63%)",     // gray-400
  };

  const colors = theme === "dark" ? DARK_COLORS : COLORS;

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[180px] text-sm text-muted-foreground">
        No data
      </div>
    );
  }

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={180}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
            animationBegin={0}
            animationDuration={800}
          >
            {data.map((entry) => (
              <Cell
                key={entry.name}
                fill={colors[entry.name]}
                strokeWidth={0}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 4,
              fontSize: 12,
              color: "hsl(var(--foreground))",
            }}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
            formatter={(value: string) => (
              <span className="text-muted-foreground">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
