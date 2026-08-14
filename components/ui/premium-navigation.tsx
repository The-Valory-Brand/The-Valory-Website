"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

export interface NavItem {
  label: string;
  href: string;
}

export const DEFAULT_NAV_ITEMS: NavItem[] = [
  { label: "HOME", href: "/" },
  { label: "SHOP", href: "/shop" },
  { label: "CATEGORY", href: "/#categories" },
];

export interface PremiumNavigationProps {
  items?: NavItem[];
  activeRoute?: string;
  className?: string;
  brandName?: string;
  tagline?: string;
  cartCount?: number;
}

export const PremiumNavigation: React.FC<PremiumNavigationProps> = ({
  items = DEFAULT_NAV_ITEMS,
  activeRoute = "/",
  className,
  brandName = "THE VALORY",
  tagline = "TIMELESS ELEGANCE",
  cartCount = 0,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isLinkActive = (href: string): boolean => {
    if (!activeRoute) return false;
    if (href === "/" && activeRoute === "/") return true;
    if (href !== "/" && activeRoute.startsWith(href)) return true;
    return false;
  };

  return (
    <header className={cn("w-full bg-black sticky top-0 z-50 transition-colors duration-300", className)}>
      <nav
        aria-label="Main navigation"
        className="mx-auto flex h-[88px] max-w-7xl items-center justify-between px-6 md:px-10"
      >
        {/* BRAND LOGO */}
        <a href="/" className="flex flex-col focus:outline-none group">
          <span className="font-serif text-xl font-bold tracking-[0.15em] text-white transition-colors duration-300 group-hover:text-amber-400">
            {brandName}
          </span>
          <span className="text-[10px] tracking-[0.3em] text-amber-500 uppercase font-semibold">
            {tagline}
          </span>
        </a>

        {/* HORIZONTALLY CENTERED DESKTOP NAVIGATION */}
        <div className="hidden md:flex items-center justify-center gap-10 lg:gap-14">
          {items.map((item) => {
            const active = isLinkActive(item.href);
            return (
              <a
                key={item.label}
                href={item.href}
                className={cn(
                  "text-xs md:text-sm font-medium uppercase tracking-[0.12em] transition-colors duration-300 py-1 focus:outline-none focus-visible:ring-1 focus-visible:ring-white",
                  active
                    ? "text-white font-semibold"
                    : "text-neutral-400 hover:text-white"
                )}
              >
                {item.label}
              </a>
            );
          })}
        </div>

        {/* RIGHT ACTIONS / MOBILE TOGGLE */}
        <div className="flex items-center gap-6">
          {/* CART ICON */}
          <a
            href="/cart"
            aria-label="Shopping Cart"
            className="relative text-neutral-300 hover:text-white transition-colors duration-300 p-1 focus:outline-none"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
              />
            </svg>
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-2 bg-amber-500 text-black text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </a>

          {/* MOBILE HAMBURGER BUTTON */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
            className="md:hidden text-neutral-300 hover:text-white focus:outline-none p-1"
          >
            {mobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </nav>

      {/* MOBILE RESPONSIVE NAVIGATION DRAWER */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-neutral-800 bg-black/95 backdrop-blur-md px-6 py-6 transition-all duration-300">
          <div className="flex flex-col gap-6 items-start">
            {items.map((item) => {
              const active = isLinkActive(item.href);
              return (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "text-sm font-medium uppercase tracking-[0.15em] transition-colors duration-300 w-full py-2",
                    active ? "text-white font-semibold border-b border-white/20" : "text-neutral-400 hover:text-white"
                  )}
                >
                  {item.label}
                </a>
              );
            })}
          </div>
        </div>
      )}
    </header>
  );
};

export default PremiumNavigation;
