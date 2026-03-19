"use client"

import { useState, useEffect } from "react";
import Footer from "@/components/footer";
import Header from "@/components/header";

export default function ZonesPage() {
  const [zones, setZones] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await fetch("/api/zones");
        if (!response.ok) throw new Error("Ошибка при загрузке данных");
        
        const data = await response.json();
        setZones(data.zones || []);
      } catch (error) {
        console.error("Failed to fetch zones:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
  }, []);

  return (
    <div className="page">
      <Header />

      <main className="main-container">
        <section className="content-section">
          <h1 className="page-title">Зоны</h1>
          
          <div className="zones-table">
            <div className="table-header">
              <span className="sortable">Название</span>
            </div>
            
            <div className="table-body">
              {loading ? (
                <div className="table-row">Загрузка...</div>
              ) : zones.length > 0 ? (
                zones.map((zoneName, index) => (
                  <div key={index} className="table-row">
                    {zoneName}
                  </div>
                ))
              ) : (
                <div className="table-row">Список зон пуст</div>
              )}
            </div>
          </div>
        </section>
      </main>

      <Footer />

      <style jsx>{`
        .main-container { padding: 60px 10%; color: white; }
        .page-title { font-size: 2rem; margin-bottom: 20px; }
        .table-header { padding: 10px 20px; color: #fff; font-weight: bold; border-bottom: 1px solid #333; }
        .table-row {  
          padding: 15px 20px; 
          margin-bottom: 8px; 
          border-bottom: 1px solid #222;
          color: #ccc;
        }
        .table-row:hover { background: #1a1a1a; }
      `}</style>
    </div>
  );
}