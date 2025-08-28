import React from 'react';
import { Outlet, NavLink, Link } from 'react-router-dom';
import { LayoutDashboard, TextSearch, Scissors, ReceiptTextIcon } from 'lucide-react';
import { assets } from '../../assets/assets';


const Layout = () => {
  const sidebarLinks = [
    { name: "Dashboard", path: "/ai", icon: LayoutDashboard },
    { name: "Text Analysis", path: "/ai/text-analysis", icon: TextSearch },
    { name: "Text Summarization", path: "/ai/text-summarization", icon: Scissors },
    { name: "Reports / Insights", path: "/ai/reports", icon: ReceiptTextIcon },
  ];
  return (
    <>
      {/* Top Navbar */}
      <div className="flex items-center justify-between px-4 py-4 md:px-8 border-b border-gray-300 bg-white transition-all duration-300">
        <Link to={'/'}>
          <img className="md:h-7 h-5 cursor-pointer" src={assets.logo} alt="Logo" />
        </Link>
        <div className="flex items-center gap-5 text-gray-500">
          
          <button className="border border-primary text-primary hover:bg-primary/10 rounded-full text-sm px-4 py-1.5 cursor-pointer">
            Logout
          </button>
        </div>
      </div>

      {/* Sidebar + Main */}
      <div className="flex">
        {/* Sidebar */}
        <div className="lg:w-64 md:w-48 w-16 border-r h-[91vh] text-base border-gray-300 pt-4 flex flex-col transition-all duration-300">
          {sidebarLinks.map((item) => {
            const Icon = item.icon; // store component in variable
            return (
              <NavLink
  to={item.path}
  key={item.name}
  end={item.path==="/ai"}
  className={({ isActive }) =>
    `flex items-center py-3 px-4 gap-3 transition
     ${isActive 
       ? "border-r-4 md:border-r-[6px] bg-primary/10 border-primary text-primary"
       : "hover:bg-gray-100/90 border-white text-gray-700"}`
  }
>
  <Icon className="w-6 h-6" />
  <p className="md:block hidden text-center">{item.name}</p>
</NavLink>
            );
          })}
        </div>

        {/* Main Content */}
        <div className="flex-1 p-4">
          <Outlet />
        </div>
      </div>
    </>
  );
};

export default Layout;
