"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface HeroSectionProps {
  subtitle?: string;
  title?: string;
  tagline?: string;
  description?: string;
  primaryButtonText?: string;
  primaryButtonHref?: string;
  secondaryButtonText?: string;
  secondaryButtonHref?: string;
  backgroundImageUrl?: string;
  className?: string;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  subtitle = "PREMIUM STREETWEAR",
  title = "TIMELESS ELEGANCE",
  description = "Elevated heavyweight essentials designed for those who move with quiet confidence and bold individuality.",
  primaryButtonText = "SHOP COLLECTION",
  primaryButtonHref = "/shop",
  secondaryButtonText = "EXPLORE TEES",
  secondaryButtonHref = "/shop?category=tees",
  backgroundImageUrl = "https://images.unsplash.com/photo-1509631179647-0177331693ae?q=80&w=1600&auto=format&fit=crop",
  className,
}) => {
  return (
    <section className={cn("relative w-full h-[85vh] min-h-[580px] max-h-[850px] bg-black overflow-hidden flex items-center", className)}>
      {/* BACKGROUND IMAGE WITH LUXURY DARK GRADIENT OVERLAY */}
      <div className="absolute inset-0 z-0">
        <img
          src={backgroundImageUrl}
          alt="THE VALORY Editorial Fashion"
          className="w-full h-full object-cover object-center opacity-60 scale-105 transition-transform duration-1000 ease-out hover:scale-100"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-black/60" />
      </div>

      {/* HERO CONTENT */}
      <div className="relative z-10 mx-auto max-w-7xl px-6 md:px-12 w-full">
        <div className="max-w-2xl text-left">
          {/* SUBTITLE */}
          <span className="inline-block text-xs md:text-sm font-semibold tracking-[0.25em] text-amber-400 uppercase mb-4">
            {subtitle}
          </span>

          {/* MAIN EDITORIAL HEADING */}
          <h1 className="font-serif text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-[0.08em] text-white uppercase leading-none mb-6">
            {title.split(" ").map((word, i) => (
              <React.Fragment key={i}>
                {word} <br className="hidden sm:inline" />
              </React.Fragment>
            ))}
          </h1>

          {/* SUPPORTING TEXT */}
          <p className="text-sm md:text-base text-neutral-300 font-light tracking-wide max-w-lg mb-8 leading-relaxed">
            "{description}"
          </p>

          {/* CALL TO ACTION BUTTONS */}
          <div className="flex flex-wrap items-center gap-4">
            <a
              href={primaryButtonHref}
              className="inline-flex items-center justify-center bg-white text-black text-xs md:text-sm font-semibold tracking-[0.18em] uppercase px-8 py-4 border border-white hover:bg-amber-400 hover:border-amber-400 hover:text-black transition-all duration-300 shadow-2xl"
            >
              {primaryButtonText}
            </a>
            <a
              href={secondaryButtonHref}
              className="inline-flex items-center justify-center bg-transparent text-white text-xs md:text-sm font-semibold tracking-[0.18em] uppercase px-8 py-4 border border-neutral-700 hover:border-amber-400 hover:text-amber-400 transition-all duration-300"
            >
              {secondaryButtonText}
            </a>
          </div>
        </div>
      </div>

      {/* SCROLL INDICATOR */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-2 opacity-70 hover:opacity-100 transition-opacity">
        <span className="text-[10px] tracking-[0.25em] uppercase text-neutral-400">Scroll</span>
        <div className="w-[1px] h-8 bg-gradient-to-b from-amber-400 to-transparent animate-pulse" />
      </div>
    </section>
  );
};

export default HeroSection;
