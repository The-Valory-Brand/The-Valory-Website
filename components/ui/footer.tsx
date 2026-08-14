"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface FooterProps {
  brandName?: string;
  tagline?: string;
  className?: string;
}

export const Footer: React.FC<FooterProps> = ({
  brandName = "THE VALORY",
  tagline = "TIMELESS ELEGANCE",
  className,
}) => {
  return (
    <footer className={cn("w-full bg-[#0A0A0A] border-t border-neutral-900 text-white pt-16 pb-12 px-6 md:px-12", className)}>
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 lg:gap-12 mb-16">
          {/* BRAND COLUMN */}
          <div className="md:col-span-2">
            <a href="/" className="inline-block mb-4">
              <span className="font-serif text-2xl font-bold tracking-[0.15em] text-white block">
                {brandName}
              </span>
              <span className="text-[10px] tracking-[0.3em] text-amber-500 uppercase font-semibold block">
                {tagline}
              </span>
            </a>
            <p className="text-xs text-neutral-400 font-light tracking-wide max-w-sm leading-relaxed mb-6">
              "Premium clothing designed for modern confidence. Heavyweight streetwear, luxury fleece hoodies, and athletic wear delivered across all over Tamil Nadu & India."
            </p>
            <div className="flex items-center gap-4">
              {["Instagram", "Facebook", "YouTube"].map((social) => (
                <a
                  key={social}
                  href={`https://${social.toLowerCase()}.com`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-semibold tracking-wider text-neutral-400 hover:text-amber-400 uppercase transition-colors"
                >
                  {social}
                </a>
              ))}
            </div>
          </div>

          {/* SHOP COLUMN */}
          <div>
            <h4 className="font-serif text-xs font-bold tracking-[0.2em] text-white uppercase mb-4">
              SHOP
            </h4>
            <ul className="flex flex-col gap-2.5 text-xs text-neutral-400 tracking-wider uppercase">
              <li><a href="/shop?category=tees" className="hover:text-white transition-colors">Tees</a></li>
              <li><a href="/shop?category=hoodies" className="hover:text-white transition-colors">Hoodies</a></li>
              <li><a href="/shop?category=jerseys" className="hover:text-white transition-colors">Jerseys</a></li>
              <li><a href="/shop?category=shirts" className="hover:text-white transition-colors">Shirts</a></li>
              <li><a href="/shop?category=trackpants" className="hover:text-white transition-colors">Trackpants</a></li>
            </ul>
          </div>

          {/* HELP COLUMN */}
          <div>
            <h4 className="font-serif text-xs font-bold tracking-[0.2em] text-white uppercase mb-4">
              HELP
            </h4>
            <ul className="flex flex-col gap-2.5 text-xs text-neutral-400 tracking-wider uppercase">
              <li><a href="/policies/shipping/" className="hover:text-white transition-colors">Tamil Nadu Shipping</a></li>
              <li><a href="/policies/refund/" className="hover:text-white transition-colors">Refund Policy</a></li>
              <li><a href="/policies/return-exchange/" className="hover:text-white transition-colors">No Return & Exchange</a></li>
              <li><a href="/policies/order/" className="hover:text-white transition-colors">Order Cancellation</a></li>
              <li><a href="/policies/general/" className="hover:text-white transition-colors">General Support</a></li>
            </ul>
          </div>

          {/* ACCOUNT & LEGAL */}
          <div>
            <h4 className="font-serif text-xs font-bold tracking-[0.2em] text-white uppercase mb-4">
              ACCOUNT
            </h4>
            <ul className="flex flex-col gap-2.5 text-xs text-neutral-400 tracking-wider uppercase mb-6">
              <li><a href="/account/profile/" className="hover:text-white transition-colors">My Profile</a></li>
              <li><a href="/orders/customer/" className="hover:text-white transition-colors">My Orders</a></li>
              <li><a href="/cart/" className="hover:text-white transition-colors">Shopping Cart</a></li>
            </ul>
            <h4 className="font-serif text-xs font-bold tracking-[0.2em] text-white uppercase mb-2">
              LOCATION
            </h4>
            <p className="text-xs text-amber-400 font-semibold tracking-wider uppercase">
              Chennai, Tamil Nadu, India
            </p>
          </div>
        </div>

        {/* BOTTOM COPYRIGHT */}
        <div className="pt-8 border-t border-neutral-900 flex flex-col sm:flex-row items-center justify-between text-[11px] text-neutral-500 tracking-widest uppercase gap-4">
          <span>&copy; 2026 {brandName}. ALL RIGHTS RESERVED.</span>
          <span>TIMELESS ELEGANCE</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
