"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface CategoryCardData {
  title: string;
  slug: string;
  image: string;
  itemCount?: number;
}

export const DEFAULT_CATEGORIES: CategoryCardData[] = [
  {
    title: "TEES",
    slug: "tees",
    image: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=800&auto=format&fit=crop",
    itemCount: 12,
  },
  {
    title: "HOODIES",
    slug: "hoodies",
    image: "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?q=80&w=800&auto=format&fit=crop",
    itemCount: 8,
  },
  {
    title: "JERSEYS",
    slug: "jerseys",
    image: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?q=80&w=800&auto=format&fit=crop",
    itemCount: 6,
  },
  {
    title: "SHIRTS",
    slug: "shirts",
    image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?q=80&w=800&auto=format&fit=crop",
    itemCount: 7,
  },
  {
    title: "TRACKPANTS",
    slug: "trackpants",
    image: "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?q=80&w=800&auto=format&fit=crop",
    itemCount: 5,
  },
];

export interface CategorySectionProps {
  title?: string;
  subtitle?: string;
  categories?: CategoryCardData[];
  className?: string;
}

export const CategorySection: React.FC<CategorySectionProps> = ({
  title = "SHOP BY CATEGORY",
  subtitle = "CURATED SELECTION",
  categories = DEFAULT_CATEGORIES,
  className,
}) => {
  return (
    <section className={cn("w-full bg-[#0A0A0A] py-20 px-6 md:px-12 border-b border-neutral-900", className)}>
      <div className="mx-auto max-w-7xl">
        {/* HEADER */}
        <div className="flex flex-col items-center text-center mb-14">
          <span className="text-xs font-semibold tracking-[0.25em] text-amber-400 uppercase mb-2">
            {subtitle}
          </span>
          <h2 className="font-serif text-3xl md:text-4xl font-bold tracking-[0.12em] text-white uppercase">
            {title}
          </h2>
          <div className="w-12 h-[2px] bg-amber-400 mt-4" />
        </div>

        {/* CATEGORY GRID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
          {categories.map((cat) => (
            <a
              key={cat.slug}
              href={`/shop?category=${cat.slug}`}
              className="group relative aspect-[3/4] w-full overflow-hidden bg-neutral-900 border border-neutral-800 flex items-end p-6 transition-all duration-500 hover:border-amber-400/50 shadow-xl"
            >
              {/* IMAGE BACKGROUND */}
              <img
                src={cat.image}
                alt={cat.title}
                className="absolute inset-0 w-full h-full object-cover object-center transition-transform duration-700 ease-out group-hover:scale-110 opacity-70 group-hover:opacity-85"
              />

              {/* OVERLAY */}
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent transition-opacity duration-300 group-hover:opacity-90" />

              {/* CARD DETAILS */}
              <div className="relative z-10 w-full flex flex-col items-start transform transition-transform duration-300 group-hover:-translate-y-1">
                <span className="text-[11px] font-medium tracking-[0.2em] text-amber-400 uppercase mb-1">
                  {cat.itemCount ? `${cat.itemCount} ITEMS` : "COLLECTION"}
                </span>
                <h3 className="font-serif text-xl font-bold tracking-[0.15em] text-white uppercase mb-2">
                  {cat.title}
                </h3>
                <span className="inline-flex items-center text-xs font-semibold tracking-[0.15em] text-neutral-300 uppercase transition-colors duration-300 group-hover:text-amber-400">
                  EXPLORE <span className="ml-1 text-sm transition-transform duration-300 group-hover:translate-x-1">→</span>
                </span>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CategorySection;
