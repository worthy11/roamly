import { Link } from "react-router-dom"     
import Layout from "./components/Layout";
import { useNavigate } from "react-router-dom";
import styles from "./Login.module.css";



function Login() {
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate("/app");
  };

  return (
    <Layout>
    <div className={styles.loginContainer}>
  <div className={styles.loginBox}>
    <h1 className={styles.loginTitle}>Login</h1>
    <form onSubmit={handleSubmit} className={styles.loginForm}>
      <label className={styles.loginLabel}>Username</label>
      <input type="text" required className={styles.loginInput} />
      <label className={styles.loginLabel}>Password</label>
      <input type="password" required className={styles.loginInput} />
      <button type="submit" className={styles.loginButton}>Confirm</button>
    </form>
    <p style={{ textAlign: "center", marginBottom: "1rem", color: "#fff", marginTop: "2rem" }}>
      Welcome back! Please login to your account
    </p>
    <Link to="/forgot-password" style={{ textAlign: "center", display: "block", color: "#d7ab75", marginBottom: "1rem" }}>
      Forgot password?
    </Link>
  </div>

  <div className={styles.loginBox}>
    <h1 className={styles.loginTitle}>Create an account</h1>
    <form onSubmit={handleSubmit} className={styles.loginForm}>
      <label className={styles.loginLabel}>Username</label>
      <input type="text" required className={styles.loginInput} />
      <label className={styles.loginLabel}>Password</label>
      <input type="password" required className={styles.loginInput} />
      <button type="submit" className={styles.loginButton}>Confirm</button>
    </form>
    <p style={{ textAlign: "center", marginBottom: "1rem", color: "#fff", marginTop: "2rem" }}>
      Start your new journey today!
    </p>
    <Link to="/forgot-password" style={{ textAlign: "center", display: "block", color: "#d7ab75", marginBottom: "1rem" }}>
      Wanna know more?
    </Link>
  </div>
</div>
</Layout>
  );
}

export default Login;