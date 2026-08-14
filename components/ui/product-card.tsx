"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

export interface ProductCardProps {
  id: number | string;
  name: string;
  slug: string;
  price: number;
  discountPrice?: number | null;
  categoryName?: string;
  imageUrl?: string;
  sizes?: string[];
  isNewArrival?: boolean;
  onAddToCart?: (productId: number | string, size: string) => void;
  onQuickView?: (productId: number | string) => void;
  className?: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  id,
  name,
  slug,
  price,
  discountPrice,
  categoryName = "THE VALORY",
  imageUrl = "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=600&auto=format&fit=crop",
  sizes = ["S", "M", "L", "XL", "XXL"],
  isNewArrival = false,
  onAddToCart,
  onQuickView,
  className,
}) => {
  const [selectedSize, setSelectedSize] = useState<string>(sizes[0] || "M");
  const [isWishlisted, setIsWishlisted] = useState<boolean>(false);

  return (
    <div
      className={cn(
        "group relative flex flex-col bg-[#141414] border border-neutral-900 overflow-hidden transition-all duration-300 hover:border-neutral-700 hover:shadow-2xl",
        className
      )}
    >
      {/* IMAGE CONTAINER WITH 4:5 ASPECT RATIO */}
      <div className="relative aspect-[4/5] w-full overflow-hidden bg-black/60">
        <a href={`/product/${slug}/`} className="block w-full h-full">
          <img
            src={imageUrl}
            alt={name}
            className="w-full h-full object-cover object-center transition-transform duration-700 ease-out group-hover:scale-105"
          />
        </a>

        {/* BADGES */}
        <div className="absolute top-3 left-3 flex flex-col gap-1 z-10">
          {isNewArrival && (
            <span className="bg-amber-400 text-black text-[10px] font-bold tracking-[0.15em] uppercase px-2.5 py-1">
              NEW
            </span>
          )}
          {discountPrice && (
            <span className="bg-red-600 text-white text-[10px] font-bold tracking-[0.15em] uppercase px-2.5 py-1">
              SALE
            </span>
          )}
        </div>

        {/* WISHLIST BUTTON */}
        <button
          type="button"
          onClick={() => setIsWishlisted(!isWishlisted)}
          aria-label="Add to Wishlist"
          className="absolute top-3 right-3 z-10 w-9 h-9 rounded-full bg-black/60 backdrop-blur-md flex items-center justify-center text-white transition-transform duration-300 hover:scale-110 focus:outline-none"
        >
          {isWishlisted ? (
            <span className="text-red-500 text-base">♥</span>
          ) : (
            <span className="text-neutral-300 text-base hover:text-white">♡</span>
          )}
        </button>

        {/* QUICK VIEW HOVER OVERLAY BUTTON */}
        <div className="absolute inset-x-0 bottom-0 p-4 bg-gradient-to-t from-black via-black/60 to-transparent translate-y-full opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 z-10 flex justify-center">
          <button
            type="button"
            onClick={() => onQuickView && onQuickView(id)}
            className="w-full bg-white/90 hover:bg-amber-400 text-black text-xs font-semibold tracking-[0.15em] uppercase py-2.5 transition-colors duration-300 backdrop-blur-sm"
          >
            QUICK VIEW
          </button>
        </div>
      </div>

      {/* PRODUCT DETAILS */}
      <div className="flex flex-col flex-1 p-5 bg-[#141414]">
        {/* CATEGORY */}
        <span className="text-[10px] font-medium tracking-[0.2em] text-neutral-400 uppercase mb-1">
          {categoryName}
        </span>

        {/* TITLE */}
        <a href={`/product/${slug}/`} className="group-hover:text-amber-400 transition-colors duration-300">
          <h3 className="font-sans text-sm font-semibold tracking-[0.05em] text-white uppercase line-clamp-1 mb-2">
            {name}
          </h3>
        </a>

        {/* PRICE */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-sm font-bold text-white tracking-wide">
            ₹{price.toLocaleString("en-IN")}
          </span>
          {discountPrice && (
            <span className="text-xs text-neutral-500 line-through">
              ₹{discountPrice.toLocaleString("en-IN")}
            </span>
          )}
        </div>

        {/* SIZE SELECTOR BADGES */}
        {sizes.length > 0 && (
          <div className="flex items-center gap-1.5 mb-4 flex-wrap">
            {sizes.map((size) => (
              <button
                key={size}
                type="button"
                onClick={() => setSelectedSize(size)}
                className={cn(
                  "text-[10px] font-medium tracking-wider w-7 h-7 flex items-center justify-center border transition-colors duration-200",
                  selectedSize === size
                    ? "border-amber-400 bg-amber-400 text-black font-bold"
                    : "border-neutral-800 text-neutral-400 hover:border-neutral-600 hover:text-white"
                )}
              >
                {size}
              </button>
            ))}
          </div>
        )}

        {/* ADD TO CART BUTTON */}
        <button
          type="button"
          onClick={() => onAddToCart && onAddToCart(id, selectedSize)}
          className="mt-auto w-full bg-neutral-900 border border-neutral-700 hover:bg-white hover:border-white hover:text-black text-white text-xs font-semibold tracking-[0.15em] uppercase py-3 transition-all duration-300"
        >
          ADD TO CART
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
