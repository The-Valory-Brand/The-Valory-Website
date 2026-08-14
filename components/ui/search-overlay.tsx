"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

export interface SearchResultItem {
  id: number | string;
  name: string;
  slug: string;
  price: number;
  category: string;
  image_url: string;
}

export interface SearchOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  results?: SearchResultItem[];
  onSearchQueryChange?: (query: string) => void;
  className?: string;
}

export const SearchOverlay: React.FC<SearchOverlayProps> = ({
  isOpen,
  onClose,
  results = [],
  onSearchQueryChange,
  className,
}) => {
  const [query, setQuery] = useState("");

  if (!isOpen) return null;

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    if (onSearchQueryChange) {
      onSearchQueryChange(val);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/95 backdrop-blur-md transition-all duration-300 p-6 md:p-12">
      <div className="mx-auto max-w-4xl flex flex-col h-full">
        {/* TOP BAR */}
        <div className="flex justify-between items-center mb-8 border-b border-neutral-800 pb-4">
          <span className="text-xs font-bold tracking-[0.25em] text-amber-400 uppercase">
            CATALOG SEARCH
          </span>
          <button
            onClick={onClose}
            aria-label="Close Search"
            className="text-neutral-400 hover:text-white text-3xl font-light focus:outline-none"
          >
            ×
          </button>
        </div>

        {/* INPUT CONTAINER */}
        <div className="relative mb-10">
          <input
            type="text"
            value={query}
            onChange={handleInput}
            placeholder="Search tees, hoodies, jerseys..."
            autoFocus
            className="w-full bg-transparent border-b-2 border-neutral-700 text-2xl md:text-4xl font-serif text-white placeholder-neutral-600 pb-4 focus:outline-none focus:border-amber-400 transition-colors tracking-wide"
          />
          <span className="absolute right-2 top-2 text-2xl text-neutral-500">🔍</span>
        </div>

        {/* POPULAR CATEGORIES (WHEN QUERY IS EMPTY) */}
        {!query && (
          <div className="mb-10">
            <span className="text-xs font-semibold tracking-[0.2em] text-neutral-400 uppercase block mb-4">
              POPULAR CATEGORIES
            </span>
            <div className="flex flex-wrap gap-3">
              {["TEES", "HOODIES", "JERSEYS", "SHIRTS", "TRACKPANTS"].map((cat) => (
                <a
                  key={cat}
                  href={`/shop?category=${cat.toLowerCase()}`}
                  onClick={onClose}
                  className="text-xs font-semibold tracking-[0.15em] uppercase text-neutral-300 bg-neutral-900 border border-neutral-800 hover:border-amber-400 hover:text-amber-400 px-5 py-2.5 transition-colors"
                >
                  {cat}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* SEARCH RESULTS GRID */}
        {query && (
          <div className="flex-1 overflow-y-auto">
            <span className="text-xs font-semibold tracking-[0.2em] text-neutral-400 uppercase block mb-6">
              MATCHING RESULTS ({results.length})
            </span>
            {results.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                {results.map((item) => (
                  <a
                    key={item.id}
                    href={`/product/${item.slug}/`}
                    onClick={onClose}
                    className="group bg-[#141414] border border-neutral-800 p-4 transition-all duration-300 hover:border-amber-400/50"
                  >
                    <img
                      src={item.image_url}
                      alt={item.name}
                      className="w-full aspect-[4/5] object-cover mb-3 bg-neutral-900"
                    />
                    <span className="text-[10px] text-neutral-500 uppercase tracking-widest block mb-1">
                      {item.category}
                    </span>
                    <h4 className="font-sans text-xs font-semibold text-white uppercase line-clamp-1 group-hover:text-amber-400 transition-colors mb-1">
                      {item.name}
                    </h4>
                    <span className="text-xs font-bold text-white tracking-wide block">
                      ₹{item.price.toLocaleString("en-IN")}
                    </span>
                  </a>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 border border-dashed border-neutral-800">
                <p className="text-xs tracking-widest text-neutral-500 uppercase">
                  NO PRODUCTS FOUND MATCHING "{query}"
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchOverlay;
