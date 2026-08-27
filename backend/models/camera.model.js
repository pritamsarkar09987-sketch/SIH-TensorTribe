import mongoose from "mongoose";

const cameraSchema = new mongoose.Schema(
  {
    cameraName: {
      type: String,
      required: true,
      trim: true,
    },

    location: {
      type: String,
      required: true,
      trim: true,
    },

    rtsp_url: {
      type: String,
      required: true,
      trim: true,
    },

    status: {
      type: String,
      enum: ["online", "offline", "maintenance"],
      default: "offline",
    },
  },
  {
    timestamps: true,
  },
);

export const Camera = mongoose.model("Camera", cameraSchema);
