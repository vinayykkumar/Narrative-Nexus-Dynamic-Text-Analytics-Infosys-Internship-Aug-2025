import { CheckCircle, CheckCircle2, CheckCircle2Icon } from "lucide-react";
import React from "react";

const Pricing = () => {
  const plans = [
    {
      name: "Basic",
      price: "$29",
      period: "/month",
      popular: false,
      bg: "bg-white/60 text-gray-800 border border-gray-200",
      textColor: "text-gray-700",
      btn: "bg-primary text-white hover:bg-indigo-600",
      features: [
        "Access to all basic courses",
        "Community support",
        "10 practice projects",
        "Course completion certificate",
        "Basic code review",
      ],
    },
    {
      name: "Pro",
      price: "$79",
      period: "/month",
      popular: true,
      bg: "bg-primary text-white border border-gray-500/30 relative",
      textColor: "text-white",
      btn: "bg-white text-primary hover:bg-gray-200",
      features: [
        "Access to all Pro courses",
        "Priority community support",
        "30 practice projects",
        "Course completion certificate",
        "Advance code review",
        "1-on-1 mentoring sessions",
        "Job assistance",
      ],
    },
    {
      name: "Enterprise",
      price: "$199",
      period: "/month",
      popular: false,
      bg: "bg-white/60 text-gray-800 border border-gray-200",
      textColor: "text-gray-700",
      btn: "bg-primary text-white hover:bg-indigo-600",
      features: [
        "Access to all courses",
        "Dedicated support",
        "Unlimited projects",
        "Course completion certificate",
        "Premium code review",
        "Weekly 1-on-1 mentoring",
        "Job guarantee",
      ],
    },
  ];

  return (
    <div id="pricing" className="px-4 py-20 sm:px-20 xl:px-32 bg-[url(bg_gradient.png)] bg-black min-h-screen">
      <div className="text-center">
        <h2 className="text-primary text-3xl md:text-5xl
         font-bold mb-4">Smart Pricing for Smarter Insights</h2>
        <p className="text-gray-300 max-w-lg mx-auto">
          Choose the plan that matches your workflow — scale effortlessly as your needs grow.
        </p>
      </div>
      <div className="flex flex-wrap mt-20 justify-center gap-8">
      {plans.map((plan, index) => (
        <div
          key={index}
          className={`w-72 p-6 rounded-xl ${
            plan.popular ? "pb-10" : "my-4"
          } ${plan.bg} text-center`}
        >
          {plan.popular && (
            <p className="absolute px-3 text-sm -top-3.5 left-3.5 py-1 bg-white/80 text-gray-800 rounded-full">
              Most Popular
            </p>
          )}
          <p className="font-semibold">{plan.name}</p>
          <h1 className="text-3xl font-semibold">
            {plan.price}
            <span className={`text-sm font-normal ${plan.textColor}`}>
              {plan.period}
            </span>
          </h1>

          <ul
            className={`list-none text-sm mt-6 space-y-1 ${
              plan.popular ? "text-white" : "text-gray-700"
            }`}
          >
            {plan.features.map((feature, i) => (
              <li key={i} className="flex items-center gap-2">
              <CheckCircle className={plan.popular ? "text-white" : "text-primary"}/>
                <p>{feature}</p>
              </li>
            ))}
          </ul>

          <button
            type="button"
            className={`text-sm w-full py-2 rounded-full mt-8 transition-all ${plan.btn}`}
          >
            Get Started
          </button>
        </div>
      ))}
      </div>
    </div>
  );
};

export default Pricing;
