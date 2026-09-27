import PriceChart from "../../components/PriceChart";
import StockAssessment from "../../components/StockAssessment";
import StockSelector from "../../components/StockSelector";

type Props = { params: Promise<{ symbol: string }> };

export default async function StockPage({ params }: Props) {
  const { symbol } = await params;
  const normalizedSymbol = symbol.toUpperCase();
  return <main className="shell"><div className="detail-wrap"><div className="detail-eyebrow mono">HİSSE DETAYI / BIST ANALİTİX</div><div className="stock-header"><div><h1>{normalizedSymbol}</h1><p>Fiyat davranışı, risk sinyalleri ve seçili temel göstergeler.</p></div><StockSelector value={normalizedSymbol} compact /></div><div className="stock-layout"><div><div className="panel stock-chart-panel"><div className="panel-heading"><div><div className="mono muted-label">FİYAT GRAFİĞİ</div><div className="detail-title">{normalizedSymbol} / TRY</div></div><span className="mono live-note">GERÇEK • GECİKMELİ</span></div><PriceChart symbol={normalizedSymbol} height={380} /></div><div className="panel fundamentals-panel"><div className="panel-heading"><div><div className="mono muted-label">TEMEL ANALİZ</div><h2>Çarpan özeti</h2></div><span className="mono muted-label">API BAĞLANTISI</span></div><div className="fundamental-grid"><span>F/K <b>8.42</b></span><span>PD/DD <b>1.64</b></span><span>FD/FAVÖK <b>5.91</b></span><span>ROE <b>%21.8</b></span></div></div></div><div><StockAssessment symbol={normalizedSymbol} /><div className="panel thesis-card"><div className="mono muted-label">ANALİST ŞABLONU</div><h2>Karar notları</h2><label>Tez <textarea placeholder="Yatırım tezini ve varsayımlarını yaz..." /></label><div className="thesis-tags"><span>Trend</span><span>Değerleme</span><span>Risk</span></div></div></div></div></div></main>;
}
