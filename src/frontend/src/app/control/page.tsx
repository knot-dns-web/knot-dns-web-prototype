import Footer from "@/components/footer";
import Header from "@/components/header";
import Link from "next/link";

export default function ControlPage() {
  return (
    <div className="page">
      <Header />

      <main className="control-main">
        <section className="control-grid">
          <Link href="/zones" className="control-card control-card--tall-left">
            Зоны
          </Link>
          <button className="control-card control-card--tall-left">
            Записи
          </button>
          <button className="control-card control-card--wide-center">
            Просмотр истории изменений
          </button>
          <button className="control-card">Настройки</button>
        </section>
      </main>

      <Footer />
    </div>
  );
}

