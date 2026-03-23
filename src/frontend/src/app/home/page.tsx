import Footer from "@/components/footer";
import Header from "@/components/header";
import InfoBlock from "./info-block";
import Link from "next/link";
import StartManagementButton from "../../components/start-management-button";

export default function HomePage() {
  return (
    <div className="page">
      <Header />

      <div className="flex-1 flex flex-col items-center p-24">
        <div className="text-center flex flex-col items-center w-full gap-3 mb-10">
          <p className="font-semibold text-3xl leading-tight">Manager KNOT DNS</p>
          <p className="text-sm text-(--light-text)">Групповой курсовой проект студентов 3 курса НИУ ВШЭ - Пермь</p>
        </div>

        <div className="flex justify-center gap-3">
          <StartManagementButton />
          <Link 
            href="https://github.com/knot-dns-web" 
            className="home-btn home-btn-outline"
          >
            <span>Исходный код на GitHub</span>
          </Link>
          <Link 
            href="https://www.knot-dns.cz"
            className="home-btn home-btn-outline">Open-source сервер</Link>
        </div>

        <InfoBlock />
      </div>

      <Footer />
    </div>
  );
}

