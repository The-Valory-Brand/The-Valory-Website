"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface BrandStoryProps {
  heading?: string;
  subheading?: string;
  content?: string;
  ctaText?: string;
  ctaHref?: string;
  imageUrl?: string;
  className?: string;
}

export const BrandStory: React.FC<BrandStoryProps> = ({
  heading = "MORE THAN WHAT YOU WEAR.",
  subheading = "CRAFTED FOR CONFIDENCE",
  content = "THE VALORY represents confidence, individuality, timeless design, and premium everyday wear. Built in Tamil Nadu, India, every piece undergoes rigorous quality control to ensure heavyweight comfort, clean structural drape, and enduring elegance.",
  ctaText = "DISCOVER OUR STORY",
  ctaHref = "/policies/general/",
  imageUrl = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1200&auto=format&fit=crop",
  className,
}) => {
  return (
    <section className={cn("w-full bg-[#0A0A0A] py-24 px-6 md:px-12 border-b border-neutral-900", className)}>
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* EDITORIAL IMAGE */}
          <div className="relative aspect-[4/5] w-full overflow-hidden bg-neutral-900 border border-neutral-800 shadow-2xl">
            <img
              src={imageUrl}
              alt="THE VALORY Brand Story"
              className="w-full h-full object-cover object-center opacity-85 transition-transform duration-700 hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            <div className="absolute bottom-6 left-6 right-6">
              <span className="text-[10px] font-bold tracking-[0.3em] text-amber-400 uppercase">
                ESTABLISHED 2026 — TAMIL NADU
              </span>
            </div>
          </div>

          {/* EDITORIAL CONTENT */}
          <div className="flex flex-col items-start text-left">
            <span className="text-xs font-semibold tracking-[0.25em] text-amber-400 uppercase mb-3">
              {subheading}
            </span>
            <h2 className="font-serif text-3xl sm:text-5xl font-extrabold tracking-[0.08em] text-white uppercase leading-tight mb-6">
              {heading}
            </h2>
            <p className="text-neutral-300 font-light text-base md:text-lg tracking-wide leading-relaxed mb-8">
              {content}
            </p>

            <div className="grid grid-cols-2 gap-6 w-full mb-10 pt-6 border-t border-neutral-800">
              <div>
                <span className="block font-serif text-2xl font-bold text-white mb-1">240 GSM</span>
                <span className="text-xs text-neutral-400 tracking-wider uppercase">Heavyweight Cotton</span>
              </div>
              <div>
                <span className="block font-serif text-2xl font-bold text-amber-400 mb-1">100% Verified</span>
                <span className="text-xs text-neutral-400 tracking-wider uppercase">Tamil Nadu Dispatch</span>
              </div>
            </div>

            <a
              href={ctaHref}
              className="inline-flex items-center justify-center bg-transparent text-white text-xs md:text-sm font-semibold tracking-[0.18em] uppercase px-8 py-4 border border-white hover:bg-amber-400 hover:border-amber-400 hover:text-black transition-all duration-300"
            >
              {ctaText} <span className="ml-2">→</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BrandStory;
