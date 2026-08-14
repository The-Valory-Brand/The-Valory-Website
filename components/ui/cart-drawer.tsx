"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface CartDrawerItem {
  id: number | string;
  product_name: string;
  product_slug: string;
  size: string;
  quantity: number;
  price: number;
  line_total: number;
  image_url: string;
}

export interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  items?: CartDrawerItem[];
  subtotal?: number;
  onUpdateQuantity?: (itemId: number | string, newQuantity: number) => void;
  onRemoveItem?: (itemId: number | string) => void;
  className?: string;
}

export const CartDrawer: React.FC<CartDrawerProps> = ({
  isOpen,
  onClose,
  items = [],
  subtotal = 0,
  onUpdateQuantity,
  onRemoveItem,
  className,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* BACKDROP OVERLAY */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity duration-300"
      />

      {/* SLIDE OVER PANEL */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className={cn("w-screen max-w-md bg-[#0A0A0A] border-l border-neutral-800 text-white flex flex-col shadow-2xl", className)}>
          {/* DRAWER HEADER */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-neutral-800">
            <h2 className="font-serif text-lg font-bold tracking-[0.15em] text-white uppercase flex items-center gap-2">
              YOUR CART <span className="text-amber-400 text-xs">({items.length})</span>
            </h2>
            <button
              onClick={onClose}
              aria-label="Close Cart"
              className="text-neutral-400 hover:text-white text-2xl leading-none focus:outline-none p-1"
            >
              ×
            </button>
          </div>

          {/* ITEM LIST */}
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
            {items.length > 0 ? (
              items.map((item) => (
                <div key={item.id} className="flex gap-4 pb-6 border-b border-neutral-900 items-center">
                  <img
                    src={item.image_url}
                    alt={item.product_name}
                    className="w-20 h-24 object-cover bg-neutral-900 border border-neutral-800"
                  />
                  <div className="flex-1 flex flex-col justify-between">
                    <div>
                      <h3 className="font-sans text-xs font-semibold tracking-wider text-white uppercase line-clamp-1 mb-1">
                        {item.product_name}
                      </h3>
                      <span className="text-[11px] text-neutral-400 tracking-widest block uppercase mb-2">
                        SIZE: <span className="text-amber-400 font-bold">{item.size}</span>
                      </span>
                    </div>

                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center border border-neutral-800">
                        <button
                          type="button"
                          onClick={() => onUpdateQuantity && onUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
                          className="w-7 h-7 flex items-center justify-center text-neutral-400 hover:text-white border-r border-neutral-800"
                        >
                          -
                        </button>
                        <span className="w-8 text-center text-xs font-bold text-white">{item.quantity}</span>
                        <button
                          type="button"
                          onClick={() => onUpdateQuantity && onUpdateQuantity(item.id, item.quantity + 1)}
                          className="w-7 h-7 flex items-center justify-center text-neutral-400 hover:text-white border-l border-neutral-800"
                        >
                          +
                        </button>
                      </div>

                      <span className="text-xs font-bold text-white tracking-wide">
                        ₹{item.line_total.toLocaleString("en-IN")}
                      </span>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => onRemoveItem && onRemoveItem(item.id)}
                    aria-label="Remove Item"
                    className="text-neutral-500 hover:text-red-500 text-xs tracking-widest uppercase self-start p-1"
                  >
                    ✕
                  </button>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center flex-1 py-20 text-center">
                <span className="text-4xl mb-4 text-neutral-600">🛒</span>
                <p className="text-sm font-medium tracking-widest text-neutral-400 uppercase mb-6">
                  YOUR SHOPPING CART IS EMPTY
                </p>
                <a
                  href="/shop"
                  onClick={onClose}
                  className="bg-white hover:bg-amber-400 text-black text-xs font-bold tracking-[0.2em] uppercase px-8 py-3.5 border border-white transition-colors"
                >
                  START SHOPPING
                </a>
              </div>
            )}
          </div>

          {/* DRAWER FOOTER */}
          {items.length > 0 && (
            <div className="p-6 border-t border-neutral-800 bg-[#141414]">
              <div className="flex justify-between items-center mb-6">
                <span className="text-xs font-semibold tracking-[0.2em] text-neutral-400 uppercase">
                  SUBTOTAL
                </span>
                <span className="text-lg font-bold text-white tracking-wide">
                  ₹{subtotal.toLocaleString("en-IN")}
                </span>
              </div>
              <div className="flex flex-col gap-3">
                <a
                  href="/cart"
                  className="w-full bg-transparent hover:bg-neutral-800 text-white text-center text-xs font-semibold tracking-[0.18em] uppercase py-3.5 border border-neutral-700 transition-colors"
                >
                  VIEW CART
                </a>
                <a
                  href="/checkout"
                  className="w-full bg-white hover:bg-amber-400 text-black text-center text-xs font-bold tracking-[0.2em] uppercase py-3.5 border border-white transition-colors shadow-lg"
                >
                  PROCEED TO CHECKOUT
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CartDrawer;
