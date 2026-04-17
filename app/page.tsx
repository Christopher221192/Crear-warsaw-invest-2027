"use client";

import { useState, useEffect } from "react";
import { Search, Building2, TrendingUp, DollarSign, ArrowRight, Zap } from "lucide-react";

interface Listing {
  id: string;
  url: string;
  price_pln_gross: number;
  price_per_sqm: number;
  rooms: number;
  area_sqm: number;
  floor: number;
  district: string;
  city: string;
  opportunity_score: number;
  annual_yield_percent: number;
}

import Chatbot from "@/components/Chatbot";
import ListingDetails from "@/components/ListingDetails";
import { AnimatePresence } from "framer-motion";

export default function Dashboard() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [selectedListing, setSelectedListing] = useState<Listing | null>(null);
  const [selectedCities, setSelectedCities] = useState<string[]>([]);

  useEffect(() => {
    fetch("/api/listings")
      .then((res) => res.json())
      .then((data) => {
        setListings(data);
        setLoading(false);
      });
  }, []);

  const filtered = listings.filter(l => 
    (selectedCities.length === 0 || selectedCities.includes(l.city)) &&
    (filter === "" || l.district.toLowerCase().includes(filter.toLowerCase()) || l.city.toLowerCase().includes(filter.toLowerCase()))
  );

  const uniqueCities = Array.from(new Set(listings.map(l => l.city))).filter(Boolean);

  const toggleCity = (city: string) => {
    setSelectedCities(prev => 
      prev.includes(city) ? prev.filter(c => c !== city) : [...prev, city]
    );
  };

  return (
    <main className="min-h-screen pb-20">
      {/* Header */}
      <header className="px-8 pt-12 pb-8 max-w-[1400px] mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-end gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-white/30 font-medium mb-2">
              Inversiones Q1/Q2 2027 · Mercado Primario
            </p>
            <h1 className="text-4xl font-extrabold tracking-tighter text-white">
              🇵🇱 Poland House <span className="gold-text">Hunter</span>
            </h1>
          </div>
          
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" />
            <input 
              type="text" 
              placeholder="Buscar ciudad o distrito..."
              className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-gold/30 transition-all"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </div>

        {/* City Filter Chips */}
        {uniqueCities.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-6 items-center">
            <span className="text-[10px] uppercase tracking-widest text-white/40 font-bold mr-2">Filtrar:</span>
            {uniqueCities.map(city => (
              <button
                key={city}
                onClick={() => toggleCity(city)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
                  selectedCities.includes(city) 
                    ? "bg-gold text-black shadow-lg shadow-gold/20" 
                    : "bg-white/5 text-white/50 border border-white/10 hover:bg-white/10"
                }`}
              >
                {city.toUpperCase()}
              </button>
            ))}
          </div>
        )}
      </header>

      {/* Stats row */}
      <section className="px-8 grid grid-cols-1 md:grid-cols-4 gap-6 max-w-[1400px] mx-auto mb-10">
        {[
          { label: "Oportunidades", value: filtered.length, icon: Building2 },
          { label: "Yield promedio", value: `${(filtered.reduce((acc, l) => acc + l.annual_yield_percent, 0) / (filtered.length || 1)).toFixed(1)}%`, icon: TrendingUp },
          { label: "Precio medio/m²", value: `${Math.round(filtered.reduce((acc, l) => acc + l.price_per_sqm, 0) / (filtered.length || 1)).toLocaleString()} PLN`, icon: DollarSign },
          { label: "Score máximo", value: Math.max(...filtered.map(l => l.opportunity_score), 0).toFixed(1), icon: Zap }
        ].map((stat, i) => (
          <div key={i} className="glass-card p-6 flex flex-col gap-1">
            <div className="flex justify-between items-center mb-1">
              <span className="text-[10px] uppercase tracking-widest text-white/30 font-semibold">{stat.label}</span>
              <stat.icon className="w-3.5 h-3.5 text-white/20" />
            </div>
            <div className="text-2xl font-bold mono tracking-tight">{stat.value}</div>
          </div>
        ))}
      </section>

      {/* Bento Grid */}
      <section className="px-8 bento-container">
        {loading ? (
          <div className="col-span-full py-20 text-center text-white/20 mono">Cargando inteligencia de mercado...</div>
        ) : filtered.map((listing) => (
          <div 
            key={listing.id} 
            onClick={() => setSelectedListing(listing)}
            className="glass-card col-span-full md:col-span-6 lg:col-span-4 p-6 group cursor-pointer hover:bg-white/[0.06]"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold tracking-tight text-white/90">{listing.district}</h3>
                <p className="text-sm text-white/40 uppercase tracking-wider font-medium">{listing.city}</p>
                <div className="mt-1 flex gap-2">
                   <button 
                     onClick={(e) => {
                       e.stopPropagation();
                       let favs = JSON.parse(localStorage.getItem('tracked_properties') || '[]');
                       if (favs.includes(listing.id)) {
                         favs = favs.filter((id) => id !== listing.id);
                         alert("Property removed from Tracking.");
                       } else {
                         favs.push(listing.id);
                         alert("Property tracked! You will be notified on price drops.");
                       }
                       localStorage.setItem('tracked_properties', JSON.stringify(favs));
                     }}
                     className="text-[9px] uppercase font-bold tracking-widest px-2 py-0.5 rounded border border-white/20 bg-white/5 hover:bg-gold hover:text-black transition-colors"
                   >
                     Track Property ❤️
                   </button>
                </div>
              </div>
              <div className="bg-gold/10 border border-gold/20 px-3 py-1 rounded-full">
                <span className="text-gold font-bold text-sm mono">{listing.opportunity_score.toFixed(1)}/100</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="flex flex-col">
                <span className="text-[10px] uppercase text-white/20 font-bold mb-1">Precio</span>
                <span className="text-lg font-bold text-gold/90 mono">{listing.price_pln_gross.toLocaleString()} PLN</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] uppercase text-white/20 font-bold mb-1">PLN/m²</span>
                <span className="text-lg font-bold text-white/70 mono">{Math.round(listing.price_per_sqm).toLocaleString()}</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-top border-white/5">
              <div className="flex gap-4 text-xs text-white/40 font-medium">
                <span>🛏️ {listing.rooms} hab.</span>
                <span>📐 {listing.area_sqm} m²</span>
              </div>
              <ArrowRight className="w-4 h-4 text-white/30 group-hover:text-gold group-hover:translate-x-1 transition-all" />
            </div>
          </div>
        ))}
      </section>

      <AnimatePresence>
        {selectedListing && (
          <ListingDetails 
            listing={selectedListing} 
            onClose={() => setSelectedListing(null)} 
          />
        )}
      </AnimatePresence>

      <Chatbot />
    </main>
  );
}
