import bcrypt from "bcryptjs";
import { pool } from "../db/connectdb.js";
import generateTokenAndSetCookie from "../utils/generateToken.js";

export const signupController = async (req, res) => {
  try {
    const { fullname, email, password, confirmPassword, gender } = req.body;

    if (!fullname || !email || !password || !confirmPassword || !gender) {
      return res.status(400).json({
        error: "Please fill all required fields!",
      });
    }

    if (password !== confirmPassword) {
      return res.status(400).json({
        error: "Passwords don't match!",
      });
    }

    // Check if user already exists
    const existingUser = await pool.query(
      `SELECT id FROM users WHERE email = $1`,
      [email],
    );

    if (existingUser.rows.length > 0) {
      return res.status(400).json({
        error: "User already exists.",
      });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Profile picture
    const boyProfilePic = `https://avatarapi.runflare.run/public/boy?usearname=[${fullname}]`;

    const girlProfilePic = `https://avatarapi.runflare.run/public/girl?usearname=[${fullname}]`;

    const generalProfilePic = `https://avatarapi.runflare.run/public?usearname=[${fullname}]`;

    const profilePic =
      gender === "male"
        ? boyProfilePic
        : gender === "female"
          ? girlProfilePic
          : generalProfilePic;

    // Create user
    const result = await pool.query(
      `INSERT INTO users
        (fullname, email, password, gender, profile_pic)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING
        id,
        fullname,
        email,
        gender,
        profile_pic`,
      [fullname, email, hashedPassword, gender, profilePic],
    );

    const newUser = result.rows[0];

    // Generate JWT
    generateTokenAndSetCookie(newUser.id, res);

    return res.status(201).json({
      _id: newUser.id,
      fullname: newUser.fullname,
      email: newUser.email,
      profilePic: newUser.profile_pic,
      gender: newUser.gender,
      message: "Signup successfully",
    });
  } catch (error) {
    console.log("Error in signup controller:", error.message);

    return res.status(500).json({
      error: "Internal server error.",
    });
  }
};

export const loginController = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        error: "Email and password are required!",
      });
    }

    // Find user
    const result = await pool.query(
      `SELECT
        id,
        fullname,
        email,
        password,
        gender,
        profile_pic
       FROM users
       WHERE email = $1`,
      [email],
    );

    const user = result.rows[0];

    if (!user) {
      return res.status(400).json({
        error: "Invalid username or password!",
      });
    }

    // Compare password
    const isPassword = await bcrypt.compare(password, user.password);

    if (!isPassword) {
      return res.status(400).json({
        error: "Invalid username or password!",
      });
    }

    // Generate JWT
    generateTokenAndSetCookie(user.id, res);

    return res.status(200).json({
      _id: user.id,
      fullname: user.fullname,
      email: user.email,
      profilePic: user.profile_pic,
      gender: user.gender,
      message: "Logged in successfully",
    });
  } catch (error) {
    console.log("Error in login controller:", error.message);

    return res.status(500).json({
      error: "Internal server error.",
    });
  }
};

export const logoutController = (req, res) => {
  try {
    res.cookie("jwt", "", {
      maxAge: 0,
    });

    return res.status(200).json({
      message: "Logged out successfully.",
    });
  } catch (error) {
    console.log("Error in logout controller:", error.message);

    return res.status(500).json({
      error: "Internal server error.",
    });
  }
};
