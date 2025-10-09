import React from "react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

export default function ReportDownload({ targetRef, filename = "SmartInsights-Report.pdf" }) {
  const handleDownload = async () => {
    try {
      const node = targetRef?.current || document.getElementById("report-area");
      if (!node) {
        alert("Nothing to export yet. Analyze some text first.");
        return;
      }

      const canvas = await html2canvas(node, {
        scale: 2,
        useCORS: true,
        backgroundColor: "#ffffff",
      });

      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      const pageW = pdf.internal.pageSize.getWidth();
      const imgW = pageW;
      const imgH = (canvas.height * pageW) / canvas.width;

      const pageH = pdf.internal.pageSize.getHeight();
      const posY = imgH < pageH ? (pageH - imgH) / 2 : 0;

      pdf.addImage(imgData, "PNG", 0, posY, imgW, imgH);
      pdf.save(filename);
    } catch (e) {
      console.error(e);
      alert("Failed to generate PDF. See console for details.");
    }
  };

  return (
    <button className="btn-action" type="button" onClick={handleDownload}>
      Download PDF
    </button>
  );
}
