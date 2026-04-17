"use client";

import { useState, useEffect } from "react";
import { Search, Building2, TrendingUp, DollarSign, ArrowRight, Zap, Star, Filter, LayoutGrid, List } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Chatbot from "@/components/Chatbot";
import ListingDetails from "@/components/ListingDetails";

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
  investment_analysis?: any;
}

export default function Dashboard() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedListing, setSelectedListing] = useState<Listing | null>(null);
  const [selectedCities, setSelectedCities] = useState<string[]>([]);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  useEffect(() => {
    fetch("/api/listings")
      .then((res) => res.json())
      .then((data) => {
        setListings(data);
        setLoading(false);
      });
    
    // Load favorites
    const saved = JSON.parse(localStorage.getItem('tracked_properties') || '[]');
    setFavorites(saved);
  }, []);

  const toggleFavorite = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const newFavs = favorites.includes(id) 
      ? favorites.filter(fid => fid !== id) 
      : [...favorites, id];
    setFavorites(newFavs);
    localStorage.setItem('tracked_properties', JSON.stringify(newFavs));
  };

  const filtered = listings.filter(l => 
    (selectedCities.length === 0 || selectedCities.includes(l.city)) &&
    (search === "" || l.district.toLowerCase().includes(search.toLowerCase()) || l.city.toLowerCase().includes(search.toLowerCase()))
  );

  const uniqueCities = Array.from(new Set(listings.map(l => l.city))).filter(Boolean);

  const toggleCity = (city: string) => {
    setSelectedCities(prev => 
      prev.includes(city) ? prev.filter(c => c !== city) : [...prev, city]
    );
  };

  return (
    <div className="relative min-h-screen bg-[#05050a] text-white selection:bg-gold/30">
      {/* Dynamic Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-gold/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full" />
      </div>

      <main className="relative z-10 max-w-[1600px] mx-auto px-6 md:px-12 py-12">
        {/* Navigation / Header */}
        <header className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8 mb-16">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <h1 className="text-5xl font-extrabold tracking-tighter mb-2">
              POLAND <span className="gold-text">HUB</span>
            </h1>
            <p className="text-white/40 text-sm font-medium tracking-widest uppercase">
              Elite Real Estate Intelligence · 2027 Projections
            </p>
          </motion.div>

          <div className="flex flex-wrap items-center gap-4 w-full lg:w-auto">
            <div className="relative flex-grow lg:w-96 group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 group-focus-within:text-gold transition-colors" />
              <input 
                type="text" 
                placeholder="Explorar distritos..."
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-gold/20 focus:border-gold/30 transition-all font-medium"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            
            <div className="flex p-1 bg-white/5 border border-white/10 rounded-xl">
               <button 
                onClick={() => setViewMode("grid")}
                className={`p-2 rounded-lg transition-all ${viewMode === "grid" ? "bg-white/10 text-gold" : "text-white/30 hover:text-white"}`}
               >
                 <LayoutGrid className="w-4 h-4" />
               </button>
               <button 
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-lg transition-all ${viewMode === "list" ? "bg-white/10 text-gold" : "text-white/30 hover:text-white"}`}
               >
                 <List className="w-4 h-4" />
               </button>
            </div>
          </div>
        </header>

        {/* Global Market Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[
            { label: "Oportunidades", value: filtered.length, icon: Building2, trend: "+12%" },
            { label: "Yield Promedio", value: `${(filtered.reduce((acc, l) => acc + l.annual_yield_percent, 0) / (filtered.length || 1)).toFixed(2)}%`, icon: TrendingUp, trend: "Stable" },
            { label: "Precio Medio", value: `${Math.round(filtered.reduce((acc, l) => acc + l.price_per_sqm, 0) / (filtered.length || 1)).toLocaleString()} PLN/m²`, icon: DollarSign, trend: "-2.4%" },
            { label: "Market Score", value: Math.max(...filtered.map(l => l.opportunity_score), 0).toFixed(1), icon: Zap, trend: "Peak" }
          ].map((stat, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="glass-card p-6 group overflow-hidden relative"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-gold/5 blur-3xl rounded-full translate-x-12 -translate-y-12" />
              <div className="flex justify-between items-start mb-4">
                <div className="p-3 bg-white/5 rounded-xl border border-white/10 group-hover:border-gold/20 transition-colors">
                  <stat.icon className="w-5 h-5 text-white/40 group-hover:text-gold transition-colors" />
                </div>
                <span className="text-[10px] font-bold text-gold/60 uppercase tracking-tighter bg-gold/5 px-2 py-1 rounded">
                  {stat.trend}
                </span>
              </div>
              <p className="text-white/30 text-[10px] font-bold uppercase tracking-widest mb-1">{stat.label}</p>
              <h3 className="text-3xl font-bold tracking-tight mono">{stat.value}</h3>
            </motion.div>
          ))}
        </div>

        {/* Filters/Tabs */}
        <div className="flex items-center gap-4 mb-8 overflow-x-auto pb-4 no-scrollbar">
          <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl opacity-40">
            <Filter className="w-3.5 h-3.5" />
            <span className="text-xs font-bold uppercase tracking-widest">Ciudades</span>
          </div>
          {uniqueCities.map(city => (
            <button
              key={city}
              onClick={() => toggleCity(city)}
              className={`whitespace-nowrap px-6 py-2.5 rounded-xl text-xs font-bold transition-all border ${
                selectedCities.includes(city) 
                  ? "bg-gold text-black border-gold shadow-lg shadow-gold/20" 
                  : "bg-white/5 text-white/40 border-white/10 hover:bg-white/10"
              }`}
            >
              {city.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Main Ranking Grid */}
        <div className={viewMode === "grid" ? "bento-container" : "flex flex-col gap-4"}>
          {loading ? (
             <div className="col-span-full py-40 flex flex-col items-center gap-4 text-white/20">
               <div className="w-12 h-12 border-2 border-gold/20 border-t-gold rounded-full animate-spin" />
               <p className="mono text-sm tracking-widest animate-pulse">SYNCHRONIZING GLOBAL DATA...</p>
             </div>
          ) : filtered.map((listing, i) => (
            <motion.div 
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: (i % 12) * 0.05 }}
              key={listing.id}
              onClick={() => setSelectedListing(listing)}
              className={`glass-card p-6 group cursor-pointer ${viewMode === "grid" ? "col-span-full md:col-span-6 lg:col-span-4" : "w-full"}`}
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-2xl font-bold tracking-tight text-white group-hover:text-gold transition-colors">{listing.district}</h3>
                    {favorites.includes(listing.id) && <Star className="w-4 h-4 fill-gold text-gold" />}
                  </div>
                  <p className="text-xs font-bold text-white/40 uppercase tracking-widest">{listing.city}</p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-lg text-xs font-bold mono group-hover:border-gold/30 transition-all">
                    SCORE: <span className="text-gold">{listing.opportunity_score.toFixed(1)}</span>
                  </div>
                  <button 
                    onClick={(e) => toggleFavorite(listing.id, e)}
                    className="p-2 bg-white/5 rounded-lg border border-white/10 hover:border-gold/30 group/fav"
                  >
                    <Star className={`w-3.5 h-3.5 transition-colors ${favorites.includes(listing.id) ? "fill-gold text-gold" : "text-white/20"}`} />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-8 mb-8">
                <div className="relative">
                  <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest mb-1">Inversión Bruta</p>
                  <p className="text-2xl font-bold text-white mono tracking-tighter">
                    {listing.price_pln_gross.toLocaleString()} <span className="text-xs text-white/30">PLN</span>
                  </p>
                </div>
                <div className="relative">
                  <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest mb-1">Rentabilidad Est.</p>
                  <p className="text-2xl font-bold text-gold mono tracking-tighter">
                    {listing.annual_yield_percent?.toFixed(2)}%
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-white/5">
                <div className="flex items-center gap-4">
                  <div className="flex flex-col">
                    <span className="text-[9px] font-bold text-white/20 uppercase">Precio/m²</span>
                    <span className="text-sm font-semibold text-white/70 mono">{Math.round(listing.price_per_sqm).toLocaleString()}</span>
                  </div>
                  <div className="w-px h-8 bg-white/5" />
                  <div className="flex flex-col">
                    <span className="text-[9px] font-bold text-white/20 uppercase">Superficie</span>
                    <span className="text-sm font-semibold text-white/70 mono">{listing.area_sqm} m²</span>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-gold transition-all duration-500">
                  <ArrowRight className="w-4 h-4 text-white/20 group-hover:text-black group-hover:translate-x-0.5 transition-all" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </main>

      <AnimatePresence>
        {selectedListing && (
          <ListingDetails 
            listing={selectedListing} 
            onClose={() => setSelectedListing(null)} 
          />
        )}
      </AnimatePresence>

      <Chatbot />
    </div>
  );
}
