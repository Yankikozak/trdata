"use client";

import { Search, Star } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

const STOCKS = [
  { symbol: "THYAO", name: "Türk Hava Yolları", sector: "Ulaştırma" },
  { symbol: "ASELS", name: "Aselsan", sector: "Savunma" },
  { symbol: "BIMAS", name: "BİM Mağazalar", sector: "Perakende" },
  { symbol: "EREGL", name: "Ereğli Demir Çelik", sector: "Metal" },
  { symbol: "KCHOL", name: "Koç Holding", sector: "Holding" },
  { symbol: "AKBNK", name: "Akbank", sector: "Bankacılık" },
  { symbol: "TUPRS", name: "Tüpraş", sector: "Enerji" },
  { symbol: "SISE", name: "Şişecam", sector: "Kimya" },
];
type Stock = (typeof STOCKS)[number];

type StockSelectorProps = { value?: string; compact?: boolean; onSelect?: (symbol: string) => void };

export default function StockSelector({ value = "THYAO", compact = false, onSelect }: StockSelectorProps) {
  const [query, setQuery] = useState("");
  const [stocks, setStocks] = useState<Stock[]>(STOCKS);
  const [isLoading, setIsLoading] = useState(true);
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${apiUrl}/api/v1/bist/universe`)
      .then((response) => response.json())
      .then((data: { symbols?: string[] }) => {
        if (!data.symbols?.length) return;
        const known = new Map(STOCKS.map((stock) => [stock.symbol, stock]));
        setStocks(data.symbols.map((symbol) => known.get(symbol) ?? { symbol, name: symbol, sector: "BIST" }));
      })
      .catch(() => undefined)
      .finally(() => setIsLoading(false));
  }, []);
  const filtered = useMemo(() => stocks.filter((stock) => `${stock.symbol} ${stock.name} ${stock.sector}`.toLocaleLowerCase("tr").includes(query.toLocaleLowerCase("tr"))), [query, stocks]);
  return <div className={`stock-selector ${compact ? "stock-selector-compact" : ""}`}>
    <div className="selector-search"><Search size={15} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Hisse veya sektör ara" aria-label="Hisse ara" /></div>
    <div className="mono selector-meta">{isLoading ? "BIST evreni yükleniyor" : `${stocks.length} BIST hissesi`}</div><div className="selector-list">{filtered.map((stock) => <Link className={`selector-option ${stock.symbol === value ? "selected" : ""}`} href={`/stocks/${stock.symbol}`} key={stock.symbol} onClick={() => onSelect?.(stock.symbol)}><span className="selector-symbol">{stock.symbol}</span><span className="selector-name">{stock.name}<small>{stock.sector}</small></span><Star size={14} /></Link>)}</div>
  </div>;
}
