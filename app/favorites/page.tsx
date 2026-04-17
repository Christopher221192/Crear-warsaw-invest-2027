"use client";

import { useState, useEffect } from "react";
import { ArrowLeft, Star, TrendingUp, DollarSign, Zap, Trash2, LayoutGrid, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

interface Listing {
  id: string;
  url: string;
  price_pln_gross: number;
  price_per_sqm: number;
  rooms: number;
  area_sqm: number;
  district: string;
  city: string;
  opportunity_score: number;
  annual_yield_percent: number;
}

export default function FavoritesPage() {
  const [allListings, setAllListings] = useState<Listing[]>([]);
  const [favorites, setFavorites] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAndFilter = async () => {
      try {
        const res = await fetch("/api/listings");
        const data = await res.json();
        setAllListings(data);
        
        const savedIds = JSON.parse(localStorage.getItem('tracked_properties') || '[]');
        const filtered = data.filter((l: Listing) => savedIds.includes(l.id));
        setFavorites(filtered);
      } catch (err) {
        console.error("Error loading favorites:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAndFilter();
  }, []);

  const removeFavorite = (id: string) => {
    const newFavs = favorites.filter(f => f.id !== id);
    setFavorites(newFavs);
    const savedIds = newFavs.map(f => f.id);
    localStorage.setItem('tracked_properties', JSON.stringify(savedIds));
  };

  return (
    <div className="relative min-h-screen bg-[#05050a] text-white selection:bg-gold/30">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-gold/5 blur-[120px] rounded-full" />
      </div>

      <main className="relative z-10 max-w-[1400px] mx-auto px-6 py-12">
        <div className="flex items-center gap-4 mb-12">
          <Link href="/" className="p-3 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all text-white/40 hover:text-white">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-4xl font-extrabold tracking-tighter">
              Mis <span className="gold-text">Favoritos</span>
            </h1>
            <p className="text-white/30 text-xs font-bold uppercase tracking-widest mt-1">Comparativa estratégica de activos</p>
          </div>
        </div>

        {loading ? (
          <div className="py-40 text-center mono text-sm text-white/20 animate-pulse">ANALYZING TRACKED ASSETS...</div>
        ) : favorites.length === 0 ? (
          <div className="glass-card py-20 flex flex-col items-center justify-center gap-6">
            <div className="p-6 bg-white/5 rounded-full border border-white/10">
              <Star className="w-10 h-10 text-white/10" />
            </div>
            <div className="text-center">
              <h3 className="text-xl font-bold mb-2">No tienes propiedades bajo seguimiento</h3>
              <p className="text-white/40 text-sm max-w-xs mx-auto">Explora el ranking principal y marca propiedades con ❤️ para compararlas aquí.</p>
            </div>
            <Link href="/" className="px-8 py-3 bg-gold text-black font-bold rounded-xl shadow-lg shadow-gold/20 hover:scale-105 transition-all">
              VOLVER AL RANKING
            </Link>
          </div>
        ) : (
          <div className="space-y-12">
            {/* Comparison Table */}
            <div className="glass-card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-white/[0.02]">
                      <th className="p-6 text-[10px] items-center gap-2 uppercase font-bold text-white/30 border-b border-white/5">Propiedad</th>
                      <th className="p-6 text-[10px] uppercase font-bold text-white/30 border-b border-white/5">Score</th>
                      <th className="p-6 text-[10px] uppercase font-bold text-white/30 border-b border-white/5">Precio</th>
                      <th className="p-6 text-[10px] uppercase font-bold text-white/30 border-b border-white/5">Yield</th>
                      <th className="p-6 text-[10px] uppercase font-bold text-white/30 border-b border-white/5">PLN/m²</th>
                      <th className="p-6 text-[10px] uppercase font-bold text-white/30 border-b border-white/5">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {favorites.map((listing) => (
                      <tr key={listing.id} className="hover:bg-white/[0.03] transition-colors border-b border-white/5 group">
                        <td className="p-6">
                          <div className="font-bold text-lg leading-tight mb-1">{listing.district}</div>
                          <div className="text-[10px] font-bold text-white/30 uppercase tracking-widest">{listing.city}</div>
                        </td>
                        <td className="p-6">
                          <div className="flex items-center gap-2">
                             <Zap className="w-3.5 h-3.5 text-gold" />
                             <span className="font-bold mono">{listing.opportunity_score.toFixed(1)}</span>
                          </div>
                        </td>
                        <td className="p-6 font-bold mono">{listing.price_pln_gross.toLocaleString()}</td>
                        <td className="p-6 font-bold mono text-gold">{listing.annual_yield_percent?.toFixed(2)}%</td>
                        <td className="p-6 font-medium text-white/60 mono">{Math.round(listing.price_per_sqm).toLocaleString()}</td>
                        <td className="p-6">
                           <button 
                            onClick={() => removeFavorite(listing.id)}
                            className="p-2 bg-white/5 border border-white/10 rounded-lg text-white/20 hover:text-red-400 hover:border-red-400/30 transition-all"
                           >
                             <Trash2 className="w-4 h-4" />
                           </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Grid View for detailed cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {favorites.map((listing) => (
                <div key={listing.id} className="glass-card p-6 flex flex-col gap-6 group relative">
                   <div className="flex justify-between items-start">
                     <div>
                       <h3 className="text-xl font-bold">{listing.district}</h3>
                       <p className="text-[10px] font-bold text-white/30 uppercase tracking-widest">{listing.city}</p>
                     </div>
                     <div className="w-10 h-10 bg-gold/5 border border-gold/10 rounded-full flex items-center justify-center font-bold text-gold text-xs mono">
                       {listing.opportunity_score.toFixed(1)}
                     </div>
                   </div>

                   <div className="space-y-4">
                      <div className="flex justify-between items-end border-b border-white/5 pb-4">
                        <span className="text-[10px] uppercase text-white/20 font-bold">Precio Inversión</span>
                        <span className="font-bold mono text-lg">{listing.price_pln_gross.toLocaleString()} PLN</span>
                      </div>
                      <div className="flex justify-between items-end border-b border-white/5 pb-4">
                        <span className="text-[10px] uppercase text-white/20 font-bold">Yield Bruto</span>
                        <span className="font-bold mono text-lg text-gold">{listing.annual_yield_percent?.toFixed(2)}%</span>
                      </div>
                   </div>

                   <Link 
                    href={listing.url} target="_blank"
                    className="w-full py-3 bg-white/5 border border-white/10 rounded-xl text-center text-xs font-bold uppercase tracking-widest hover:bg-gold hover:text-black hover:border-gold transition-all"
                   >
                     Ver Anuncio Original
                   </Link>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
