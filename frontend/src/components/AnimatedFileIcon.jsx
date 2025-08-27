import { motion } from "framer-motion";
import { FaFileAlt } from "react-icons/fa";

export function AnimatedFileIcon() {
  return (
    <motion.div
      animate={{ rotate: [0, 360] }}
      transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
      className="text-5xl mb-1 text-cyan-400 mx-auto"
      style={{display:'inline-block'}}
    >
      <FaFileAlt />
    </motion.div>
  );
}
