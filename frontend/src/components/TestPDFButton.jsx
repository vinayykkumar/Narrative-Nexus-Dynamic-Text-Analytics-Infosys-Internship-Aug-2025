import jsPDF from "jspdf";
import "jspdf-autotable";

export default function TestPDFButton() {
  const exportReport = () => {
    const doc = new jsPDF();
    doc.autoTable({
      head: [["A", "B"]],
      body: [["1", "2"], ["3", "4"]]
    });
    doc.save("test.pdf");
  };
  return <button onClick={exportReport}>Test PDF</button>;
}
