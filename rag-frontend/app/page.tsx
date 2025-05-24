import CompareView from "./components/CompareView";

export default function Home() {
  return (
    <>
      <CompareView />
      <a
        href="https://github.com/ayushdangi2003"
        target="_blank"
        rel="noopener noreferrer"
        className="fixed bottom-4 right-4 bg-black text-white px-4 py-2 rounded shadow-lg hover:bg-gray-800 z-50"
      >
        ⭐ Star My GitHub
      </a>
    </>
  );
}
