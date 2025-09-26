import Navbar from "./Navbar";
import "./Layout.css";

function Layout({ children }) {
  return (
      <div>
       <Navbar />
         <main>{children}</main>
      </div>
    
  );
}

export default Layout;