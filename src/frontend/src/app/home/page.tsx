import Footer from "@/components/footer";
import Header from "@/components/header";
import InfoBlock from "./info-block";

export default function HomePage() {
  return (
    <div className="page">
      <Header />

      <main className="home-main">
        <section className="home-hero">
          <h1 className="home-title">Название проекта</h1>
          <p className="home-subtitle">Самый крутой курсовой проект</p>
        </section>

        <section className="home-actions">
          <button className="home-btn home-btn-primary">Начать управление</button>
          <button className="home-btn home-btn-outline">Исходный код на GitHub</button>
          <button className="home-btn home-btn-outline">Open-source сервер</button>
        </section>

        <InfoBlock />
      </main>

      <Footer />
    </div>
  );
}

