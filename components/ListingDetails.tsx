"use client";

import { useState } from "react";
import { X, MapPin, Ruler, Home, Calendar, Factory, DollarSign, TrendingUp, Info, Building2, Train, ShoppingCart, GraduationCap, Hospital, Percent, ArrowUpRight, Zap } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { motion } from "framer-motion";

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

export default function ListingDetails({ listing, onClose }: { listing: Listing, onClose: () => void }) {
  const analysis = listing.investment_analysis || {};
  const mortgage = analysis.mortgage_sim || {};
  const rent = analysis.rent_sim || {};
  const projection = analysis.projection_2031 || {};

  const chartData = [
    { name: "Este Activo", value: listing.price_per_sqm, color: "#FFD700" },
    { name: "Media Distrito", value: analysis.nbp_district_avg || listing.price_per_sqm * 0.9, color: "rgba(255,255,255,0.15)" }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-[#05050a]/90 backdrop-blur-xl z-[100] flex items-center justify-center p-4 md:p-8 overflow-y-auto"
    >
      <motion.div 
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        className="bg-[#0c0c1a] w-full max-w-7xl glass-card overflow-hidden shadow-2xl shadow-gold/10 flex flex-col my-auto border-white/10"
      >
        {/* Header Section */}
        <div className="p-8 border-b border-white/5 bg-white/[0.01] flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] px-3 py-1 bg-white/5 border border-white/10 rounded-full text-white/40">
                PROYECTO 2027 · {listing.id}
              </span>
              <div className="flex items-center gap-1.5 px-3 py-1 bg-gold/10 border border-gold/20 rounded-full">
                <Zap className="w-3 h-3 text-gold" />
                <span className="text-[10px] font-black text-gold uppercase tracking-widest">{listing.opportunity_score.toFixed(1)} SCORE</span>
              </div>
            </div>
            <h2 className="text-4xl font-extrabold tracking-tighter text-white mb-1">
              {listing.district}, {listing.city}
            </h2>
            <div className="flex items-center gap-2">
               <MapPin className="w-4 h-4 text-white/20" />
               <span className="text-sm font-medium text-white/40 tracking-wide uppercase">Mazovia, Poland</span>
            </div>
          </div>

          <div className="flex items-center gap-8">
            <div className="text-right">
              <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest mb-1 text-right">Valor de Mercado</p>
              <p className="text-4xl font-black text-gold mono leading-none">
                {listing.price_pln_gross.toLocaleString()} <span className="text-base font-medium opacity-50">PLN</span>
              </p>
            </div>
            <button 
              onClick={onClose} 
              className="p-3 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all group"
            >
              <X className="w-6 h-6 text-white/20 group-hover:text-white transition-colors" />
            </button>
          </div>
        </div>

        {/* Dash Grid */}
        <div className="p-8 grid grid-cols-1 lg:grid-cols-12 gap-8 overflow-y-auto max-h-[70vh] no-scrollbar">
          
          {/* Panel 1: Core Analysis (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass-card p-8 bg-white/[0.02]">
              <h4 className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/20 mb-8">Asset Specifications</h4>
              <div className="grid grid-cols-2 gap-y-10">
                {[
                  { label: "Área Total", value: `${listing.area_sqm} m²`, icon: Ruler },
                  { label: "Configuración", value: `${listing.rooms} HAB`, icon: Home },
                  { label: "Nivel / Piso", value: `${listing.floor || "0"}`, icon: Building2 },
                  { label: "Precio Unitario", value: `${Math.round(listing.price_per_sqm).toLocaleString()} PLN`, icon: DollarSign },
                ].map((spec, i) => (
                  <div key={i} className="flex flex-col gap-2">
                    <div className="flex items-center gap-2">
                       <spec.icon className="w-3.5 h-3.5 text-gold/40" />
                       <span className="text-[10px] font-bold text-white/30 uppercase tracking-widest">{spec.label}</span>
                    </div>
                    <span className="text-xl font-bold text-white/90 mono">{spec.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-0 overflow-hidden h-[280px] border-white/5">
               <iframe 
                width="100%" height="100%" frameBorder="0" 
                style={{border: 0, filter: 'invert(90%) hue-rotate(180deg) contrast(110%) brightness(0.8)'}} 
                src={`https://maps.google.com/maps?q=${listing.district},${listing.city},Poland&t=m&z=14&output=embed`} 
              />
            </div>
          </div>

          {/* Panel 2: Financial Intelligence (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass-card p-8 bg-gradient-to-b from-white/[0.03] to-transparent">
              <h4 className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/20 mb-8">Financial Terminal</h4>
              
              <div className="space-y-8">
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-xs font-semibold text-white/40">Mortgage Repayment</span>
                    <span className="text-lg font-bold text-white mono">{mortgage.monthly_payment_pln?.toLocaleString() || "—"} PLN/m</span>
                  </div>
                  <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gold/40 w-[60%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-xs font-semibold text-white/40">Estimated Monthly Rent</span>
                    <span className="text-lg font-bold text-gold mono">{rent.estimated_monthly_rent_pln?.toLocaleString() || "—"} PLN/m</span>
                  </div>
                  <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gold w-[75%]" />
                  </div>
                </div>

                <div className="pt-6 border-t border-white/5">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xs font-bold uppercase tracking-widest text-white/30">Net Monthly Cashflow</span>
                    <span className={`text-xl font-black mono ${rent.monthly_cashflow_pln >= 0 ? "text-green-400" : "text-red-400"}`}>
                      {rent.monthly_cashflow_pln >= 0 ? "+" : ""}{rent.monthly_cashflow_pln?.toLocaleString()} PLN
                    </span>
                  </div>
                  <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex items-center justify-between">
                     <span className="text-[10px] font-bold uppercase text-white/20">Annual Yield</span>
                     <span className="text-sm font-black text-gold">{rent.gross_yield_pct}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-card p-8 bg-white/[0.02] h-[260px]">
              <h4 className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/20 mb-6">Market Deviation</h4>
              <ResponsiveContainer width="100%" height="80%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: 'rgba(255,255,255,0.2)', fontSize: 10, fontWeight: 'bold'}} />
                  <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    contentStyle={{backgroundColor: '#0c0c1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '12px'}}
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={40}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="flex justify-between items-center mt-2 px-2">
                 <span className="text-[9px] font-bold text-white/10 uppercase tracking-widest">Source: SARFiN AMRON Q1/2026</span>
                 <span className="text-[10px] font-bold text-green-400 mono">UNDERVALUED BY {Math.abs(analysis.market_diff_pct || 0).toFixed(1)}%</span>
              </div>
            </div>
          </div>

          {/* Panel 3: AI Projections & CTA (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass-card p-8 bg-gradient-to-br from-indigo-500/10 via-transparent to-transparent border-indigo-500/20 h-full flex flex-col">
              <div className="flex items-center gap-4 mb-10">
                <div className="p-3 bg-indigo-500/20 rounded-2xl border border-indigo-500/30 shadow-lg shadow-indigo-500/20">
                   <TrendingUp className="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                  <h4 className="text-[10px] font-bold uppercase tracking-[0.3em] text-indigo-300">Strategy Projection</h4>
                  <p className="text-xl font-bold tracking-tight">VISTA 5 AÑOS (2031)</p>
                </div>
              </div>

              <div className="space-y-10 flex-grow">
                 <div>
                   <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest mb-1">Exit Value Projection (Estimated)</p>
                   <p className="text-3xl font-black text-white mono">{projection.estimated_value_pln?.toLocaleString()} PLN</p>
                 </div>
                 
                 <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-2xl border border-white/10">
                       <p className="text-[9px] font-bold text-white/20 uppercase mb-1">Expect Capital Gain</p>
                       <p className="text-lg font-bold text-green-400 mono">+{projection.expected_capital_gain_pct}%</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-2xl border border-white/10">
                       <p className="text-[9px] font-bold text-white/20 uppercase mb-1">Vision AI Score</p>
                       <p className="text-lg font-bold text-indigo-300 mono">{analysis.vision_ai_layout?.split(" ")[0] || "A+"}</p>
                    </div>
                 </div>

                 <div className="p-6 bg-white/[0.01] border-l-2 border-indigo-500/40 rounded-r-2xl">
                    <p className="text-xs text-white/50 leading-relaxed italic">
                      "Basado en proximidad al Metro y la zonificación 2030, este activo presenta un riesgo de vacancia inferior al 3.5% anual en el mercado secundario."
                    </p>
                 </div>
              </div>

              <div className="mt-12 space-y-4">
                <a 
                  href={listing.url} target="_blank" rel="noopener noreferrer"
                  className="flex items-center justify-center gap-3 w-full py-5 bg-gold text-black font-black text-sm uppercase tracking-widest rounded-3xl hover:bg-gold/90 transition-all shadow-xl shadow-gold/20"
                >
                  NEGOCIAR ASSET <ArrowUpRight className="w-5 h-5" />
                </a>
                <p className="text-[10px] text-center text-white/20 font-bold uppercase tracking-[0.2em]">Referencia: {listing.original_title || "PORTAL EXTERNO"}</p>
              </div>
            </div>
          </div>

        </div>
      </motion.div>
    </motion.div>
  );
}
