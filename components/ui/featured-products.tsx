"use client";

import React from "react";
import { ProductCard, ProductCardProps } from "./product-card";
import { cn } from "@/lib/utils";

export interface FeaturedProductsProps {
  title?: string;
  subtitle?: string;
  products?: ProductCardProps[];
  onAddToCart?: (productId: number | string, size: string) => void;
  onQuickView?: (productId: number | string) => void;
  className?: string;
}

export const FeaturedProducts: React.FC<FeaturedProductsProps> = ({
  title = "THE VALORY EDIT",
  subtitle = "FEATURED ESSENTIALS",
  products = [],
  onAddToCart,
  onQuickView,
  className,
}) => {
  return (
    <section className={cn("w-full bg-black py-20 px-6 md:px-12 border-b border-neutral-900", className)}>
      <div className="mx-auto max-w-7xl">
        {/* HEADER */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 border-b border-neutral-800 pb-6 gap-4">
          <div>
            <span className="text-xs font-semibold tracking-[0.25em] text-amber-400 uppercase mb-2 block">
              {subtitle}
            </span>
            <h2 className="font-serif text-3xl md:text-4xl font-bold tracking-[0.12em] text-white uppercase">
              {title}
            </h2>
          </div>
          <a
            href="/shop"
            className="inline-flex items-center text-xs font-semibold tracking-[0.18em] text-neutral-300 hover:text-amber-400 uppercase transition-colors duration-300"
          >
            VIEW ALL PRODUCTS <span className="ml-2">→</span>
          </a>
        </div>

        {/* PRODUCT GRID */}
        {products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                {...product}
                onAddToCart={onAddToCart}
                onQuickView={onQuickView}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 border border-dashed border-neutral-800">
            <p className="text-sm font-medium tracking-widest text-neutral-500 uppercase">
              NO FEATURED PRODUCTS AVAILABLE AT THE MOMENT
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default FeaturedProducts;
