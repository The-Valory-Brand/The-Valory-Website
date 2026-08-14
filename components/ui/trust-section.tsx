"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface TrustItem {
  title: string;
  description: string;
  icon: string;
}

export const DEFAULT_TRUST_ITEMS: TrustItem[] = [
  {
    title: "PREMIUM QUALITY",
    description: "Carefully selected 240+ GSM heavyweight fabrics with reinforced stitching.",
    icon: "💎",
  },
  {
    title: "SECURE PAYMENTS",
    description: "100% encrypted & cryptographically secure checkout experience.",
    icon: "🔒",
  },
  {
    title: "FAST DELIVERY",
    description: "Reliable dispatch across all cities in Tamil Nadu & Pan-India.",
    icon: "🚚",
  },
  {
    title: "CUSTOMER SUPPORT",
    description: "Dedicated assistance for sizing, shipping, and pre-dispatch orders.",
    icon: "🛡️",
  },
];

export interface TrustSectionProps {
  heading?: string;
  subheading?: string;
  items?: TrustItem[];
  className?: string;
}

export const TrustSection: React.FC<TrustSectionProps> = ({
  heading = "DESIGNED IN INDIA. DELIVERED ACROSS INDIA.",
  subheading = "THE VALORY GUARANTEE",
  items = DEFAULT_TRUST_ITEMS,
  className,
}) => {
  return (
    <section className={cn("w-full bg-[#141414] py-16 px-6 md:px-12 border-b border-neutral-900", className)}>
      <div className="mx-auto max-w-7xl">
        {/* BANNER HEADER */}
        <div className="text-center mb-12">
          <span className="text-xs font-semibold tracking-[0.25em] text-amber-400 uppercase mb-2 block">
            {subheading}
          </span>
          <h2 className="font-serif text-2xl md:text-3xl font-bold tracking-[0.12em] text-white uppercase">
            {heading}
          </h2>
        </div>

        {/* 4-COLUMN TRUST GRID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {items.map((item, idx) => (
            <div
              key={idx}
              className="flex flex-col items-center text-center p-6 bg-black/40 border border-neutral-800/80 transition-all duration-300 hover:border-amber-400/40"
            >
              <div className="text-3xl mb-4 text-amber-400">{item.icon}</div>
              <h3 className="font-serif text-sm font-bold tracking-[0.15em] text-white uppercase mb-2">
                {item.title}
              </h3>
              <p className="text-xs text-neutral-400 font-light leading-relaxed">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TrustSection;
