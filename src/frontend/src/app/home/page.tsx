import Footer from "@/components/footer";
import Header from "@/components/header";
import InfoBlock from "./info-block";
import Link from "next/link";
import StartManagementButton from "./start-management-button";

export default function HomePage() {
  return (
    <div className="page">
      <Header />

      <main className="home-main">
        <section className="text-center flex flex-col items-center w-full gap-3 mb-10">
          <p className="home-title">KNOT DeNiS.ru</p>
          <p className="home-subtitle">Самый крутой курсовой проект</p>
        </section>

        <div className="flex justify-center gap-3">
          <StartManagementButton />
          <Link 
            href="https://github.com/knot-dns-web" 
            className="home-btn home-btn-outline"
          >
            <span>Исходный код на GitHub</span>
          </Link>
          <button className="home-btn home-btn-outline">Open-source сервер</button>
        </div>

        <InfoBlock />
      </main>

      <Footer />
    </div>
  );
}

