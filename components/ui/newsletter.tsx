"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";

export interface NewsletterProps {
  title?: string;
  description?: string;
  buttonText?: string;
  placeholderText?: string;
  className?: string;
}

export const Newsletter: React.FC<NewsletterProps> = ({
  title = "STAY IN THE VALORY",
  description = "Be the first to discover new drops, exclusive releases and updates.",
  buttonText = "SUBSCRIBE",
  placeholderText = "ENTER YOUR EMAIL",
  className,
}) => {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim()) {
      setSubscribed(true);
    }
  };

  return (
    <section className={cn("w-full bg-black py-20 px-6 md:px-12 border-b border-neutral-900", className)}>
      <div className="mx-auto max-w-3xl text-center">
        <span className="text-xs font-semibold tracking-[0.25em] text-amber-400 uppercase mb-3 block">
          EXCLUSIVES & DROPS
        </span>
        <h2 className="font-serif text-3xl md:text-5xl font-bold tracking-[0.12em] text-white uppercase mb-4">
          {title}
        </h2>
        <p className="text-sm md:text-base text-neutral-400 font-light tracking-wide mb-8">
          {description}
        </p>

        {subscribed ? (
          <div className="p-4 border border-amber-400/50 bg-amber-400/10 text-amber-300 text-sm tracking-widest uppercase font-semibold">
            THANK YOU FOR SUBSCRIBING TO THE VALORY RELEASES.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-center gap-3 w-full max-w-md mx-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={placeholderText}
              required
              className="w-full bg-[#141414] border border-neutral-800 text-white placeholder-neutral-500 text-xs font-medium tracking-[0.15em] px-5 py-4 focus:outline-none focus:border-amber-400 transition-colors"
            />
            <button
              type="submit"
              className="w-full sm:w-auto bg-white hover:bg-amber-400 text-black text-xs font-bold tracking-[0.2em] uppercase px-8 py-4 border border-white hover:border-amber-400 transition-colors whitespace-nowrap"
            >
              {buttonText}
            </button>
          </form>
        )}
      </div>
    </section>
  );
};

export default Newsletter;
