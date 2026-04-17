"use client";

import { useState } from "react";
import { X, MapPin, Ruler, Home, Calendar, Factory, Percent, DollarSign, TrendingUp, Info, Building2, LayoutDashboard, Train, ShoppingCart, GraduationCap, Hospital } from "lucide-react";
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
  total_floors: number;
  district: string;
  city: string;
  opportunity_score: number;
  annual_yield_percent: number;
  price_vs_avg_percent: number;
  estimated_monthly_rent: number;
  developer: string;
  delivery_date: string;
  phase: string;
  lat: number;
  lon: number;
  poi_transport: number;
  poi_supermarket: number;
  poi_school: number;
  poi_hospital: number;
  spatial_benchmark_text: string;
  layout_pros: string[];
  layout_cons: string[];
  ai_insight_text: string;
}

export default function ListingDetails({ listing, onClose }: { listing: Listing, onClose: () => void }) {
  const [downPaymentPct, setDownPaymentPct] = useState(20);
  const [termYears, setTermYears] = useState(20);

  const calculateMortgage = () => {
    const loanAmount = listing.price_pln_gross * (1 - downPaymentPct / 100);
    const monthlyRate = 0.0575 / 12;
    const numPayments = termYears * 12;
    return (monthlyRate * loanAmount) / (1 - Math.pow(1 + monthlyRate, -numPayments));
  };

  const mortgage = calculateMortgage();
  const cashflow = listing.estimated_monthly_rent - mortgage;

  const chartData = [
    { name: "Este inmueble", value: listing.price_per_sqm, color: "#FFD700" },
    { name: "Media Distrito", value: listing.price_per_sqm / (1 + (listing.price_vs_avg_percent || 0) / 100), color: "rgba(255,255,255,0.3)" }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] flex items-center justify-center p-4 md:p-8"
    >
      <div className="bg-[#0c0c1a] w-full max-w-6xl h-full max-h-[90vh] glass-card overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-white/10 flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] uppercase tracking-widest text-white/30 font-bold px-2 py-0.5 border border-white/10 rounded">
                Portal: OTODOM
              </span>
              <span className="text-[10px] uppercase tracking-widest text-white/30 font-bold px-2 py-0.5 border border-white/10 rounded">
                ID: {listing.id}
              </span>
            </div>
            <h2 className="text-3xl font-extrabold tracking-tight text-white mb-1">
              {listing.district}, {listing.city}
            </h2>
            <p className="text-gold font-bold text-2xl mono">
              {listing.price_pln_gross.toLocaleString()} <span className="text-sm font-medium">PLN</span>
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
            <X className="w-6 h-6 text-white/40" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Specs & Features */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass-card p-6">
              <h4 className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-4">Especificaciones</h4>
              <div className="grid grid-cols-2 gap-y-4 gap-x-6">
                {[
                  { label: "Superficie", value: `${listing.area_sqm} m²`, icon: Ruler },
                  { label: "Habitaciones", value: listing.rooms, icon: Home },
                  { label: "Piso", value: `${listing.floor}/${listing.total_floors || '?'}`, icon: Building2 },
                  { label: "Promotor", value: listing.developer || '—', icon: Factory },
                  { label: "Entrega", value: listing.delivery_date || '—', icon: Calendar },
                  { label: "Precio/m²", value: `${Math.round(listing.price_per_sqm).toLocaleString()}`, icon: DollarSign },
                ].map((spec, i) => (
                  <div key={i} className="flex flex-col gap-1">
                    <span className="text-[9px] uppercase text-white/20 font-bold">{spec.label}</span>
                    <span className="text-sm font-medium text-white/80">{spec.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card mt-6 overflow-hidden h-[200px] relative p-0 border border-white/10">
              <div className="absolute top-4 left-4 z-10 bg-black/50 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-2 pointer-events-none">
                <MapPin className="w-3 h-3 text-gold" />
                <span className="text-[10px] uppercase tracking-widest text-white/80 font-bold">Ubicación</span>
              </div>
              <iframe 
                width="100%" 
                height="100%" 
                frameBorder="0" 
                style={{border: 0, filter: 'invert(90%) hue-rotate(180deg) contrast(85%) opacity(80%)'}} 
                src={`https://maps.google.com/maps?q=${listing.lat && listing.lon ? `${listing.lat},${listing.lon}` : encodeURIComponent(listing.district + ', ' + listing.city + ', Poland')}&t=m&z=14&output=embed`} 
                title="mapa"
              ></iframe>
            </div>

            <div className="glass-card p-6 mt-6">
              <h4 className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-4 flex gap-2 items-center">
                <Building2 className="w-3 h-3 text-white/20" />
                Conectividad y Amenidades
              </h4>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Transporte", value: `A ${listing.poi_transport || 3} min`, icon: Train },
                  { label: "Supermercado", value: `A ${listing.poi_supermarket || 5} min`, icon: ShoppingCart },
                  { label: "Colegio", value: `A ${listing.poi_school || 10} min`, icon: GraduationCap },
                  { label: "Hospital", value: `A ${listing.poi_hospital || 15} min`, icon: Hospital },
                ].map((poi, i) => (
                  <div key={i} className="flex flex-col gap-1">
                    <span className="flex items-center gap-1.5 text-[10px] uppercase text-white/30 font-bold">
                      <poi.icon className="w-3 h-3 text-white/20" />
                      {poi.label}
                    </span>
                    <span className="text-sm font-medium text-white/80">{poi.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-6 bg-gold/[0.02] border-gold/10 mt-6">
              <h4 className="text-[10px] uppercase tracking-widest text-gold/40 font-bold mb-4">Métricas de Inversión</h4>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white/50">Opportunity Score</span>
                  <span className="text-lg font-bold text-gold mono">{listing.opportunity_score.toFixed(1)}/10</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white/50">Yield Anual Est.</span>
                  <span className="text-lg font-bold text-white/80 mono">{listing.annual_yield_percent?.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white/50">vs. Media Distrito</span>
                  <span className={`text-sm font-bold mono ${listing.price_vs_avg_percent <= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {listing.price_vs_avg_percent > 0 ? '+' : ''}{listing.price_vs_avg_percent?.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Middle Column: Market Charts */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass-card p-6 h-[260px]">
              <h4 className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-6">Comparativa de Mercado (PLN/m²)</h4>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: 'rgba(255,255,255,0.4)', fontSize: 10}} />
                  <Tooltip 
                    contentStyle={{backgroundColor: '#0c0c1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px'}}
                    itemStyle={{color: '#gold'}}
                  />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <p className="text-[9px] text-white/20 mt-1 text-right tracking-widest uppercase">
                Fuente: NBP & rynekpierwotny.pl (Abril 2026)
              </p>
            </div>

            <div className="glass-card p-6">
              <h4 className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-4 flex items-center justify-between">
                Simulador Hipotecario (WIBOR 3M 3.85% + Margen)
                <Info className="w-3 h-3 text-white/20" />
              </h4>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-[10px] text-white/30 font-bold mb-2 uppercase">
                    <span>Entrada (Down Payment): 20% Fijo</span>
                    <span>Plazo: 30 años</span>
                  </div>
                  <input 
                    type="range" min="20" max="20" step="1" value={20} disabled
                    className="w-full accent-gold h-1 bg-white/10 rounded-lg appearance-none cursor-pointer opacity-50"
                  />
                </div>
                
                <div className="pt-4 space-y-2 border-t border-white/5">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-white/40">Cuota mensual</span>
                    <span className="text-sm font-bold text-gold mono">{listing.investment_analysis?.mortgage_sim?.monthly_payment_pln?.toLocaleString()} PLN</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-white/40">Alquiler est.</span>
                    <span className="text-sm font-medium text-white/80 mono">{listing.investment_analysis?.rent_sim?.estimated_monthly_rent_pln?.toLocaleString()} PLN</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="text-xs text-white/60 font-bold">Cashflow neto</span>
                    <span className={`text-sm font-bold mono ${listing.investment_analysis?.rent_sim?.monthly_cashflow_pln >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {listing.investment_analysis?.rent_sim?.monthly_cashflow_pln >= 0 ? '+' : ''}{listing.investment_analysis?.rent_sim?.monthly_cashflow_pln?.toLocaleString()} PLN
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: AI Insights */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass-card p-6 h-full bg-gradient-to-br from-indigo-500/5 to-purple-500/5 flex flex-col">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-indigo-400" />
                </div>
                <h4 className="text-[10px] uppercase tracking-widest text-white/30 font-bold">Proyección de Plusvalía (2031)</h4>
              </div>
              
              <div className="space-y-4 mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white/50">Valor Estimado 2031</span>
                  <span className="text-lg font-bold text-gold mono">{listing.investment_analysis?.projection_2031?.estimated_value_pln?.toLocaleString()} PLN</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white/50">Plusvalía Neta</span>
                  <span className="text-sm font-bold text-green-400 mono">+{listing.investment_analysis?.projection_2031?.expected_capital_gain_pln?.toLocaleString()} PLN</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-white/50">Crecimiento (5 Años)</span>
                  <span className="text-sm font-bold text-white/80 mono">{listing.investment_analysis?.projection_2031?.expected_capital_gain_pct?.toFixed(2)}%</span>
                </div>
              </div>

              <div className="mb-6 border-t border-white/10 pt-6">
                <h4 className="text-[10px] uppercase tracking-widest text-white/30 font-bold mb-4 flex items-center gap-2">
                  <LayoutDashboard className="w-3 h-3 text-white/20" />
                  Análisis Espacial Vision AI
                </h4>
                <div className="space-y-4 text-sm text-white/60">
                  <p className="text-xs">
                    <span className="text-white/90 font-bold">Distribución:</span> {listing.investment_analysis?.vision_ai_layout || 'Desconocida'}
                  </p>
                </div>
              </div>

              <div className="space-y-4 mt-auto">
                <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                  <p className="text-[10px] uppercase text-white/30 font-bold mb-2">Break-Even (Alquiler vs Compra)</p>
                  <p className="text-sm font-bold text-indigo-300">El alquiler paga el 100% de la casa en {listing.investment_analysis?.rent_sim?.break_even_years_from_rent} años.</p>
                </div>
                <a 
                  href={listing.url} target="_blank" rel="noopener noreferrer"
                  className="block w-full py-4 bg-gold hover:bg-gold/90 text-black font-bold text-center rounded-xl transition-all shadow-lg shadow-gold/20"
                >
                  VER ANUNCIO ORIGINAL
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
