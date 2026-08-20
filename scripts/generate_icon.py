import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_kayzit_icon():
    os.makedirs("resources", exist_ok=True)
    
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background Shield / Rounded Hexagon with Neon Cyan Glow
    # Outer Glow
    for i in range(15, 0, -2):
        alpha = int(120 * (1 - i / 15))
        glow_box = [30 - i, 30 - i, 482 + i, 482 + i]
        draw.rounded_rectangle(glow_box, radius=90 + i, outline=(32, 184, 242, alpha), width=3)

    # Base Solid Shield / Dark Graphite Panel
    draw.rounded_rectangle([30, 30, 482, 482], radius=90, fill=(16, 20, 28, 255), outline=(32, 184, 242, 230), width=8)

    # Inner Subtle Border
    draw.rounded_rectangle([48, 48, 464, 464], radius=76, outline=(213, 225, 240, 35), width=2)

    # 2. Parallel Signal Wave Lines (Control Room Telemetry motif)
    wave_color = (32, 184, 242, 70)
    for y_offset in [170, 256, 342]:
        draw.line([(80, y_offset), (432, y_offset)], fill=wave_color, width=2)
        # Small node dots
        draw.ellipse([76, y_offset-4, 84, y_offset+4], fill=(65, 230, 165, 200))
        draw.ellipse([428, y_offset-4, 436, y_offset+4], fill=(65, 230, 165, 200))

    # 3. Stylized "K" & Central Lightning Bolt (Signal Cyan & Electric White)
    # Draw Bold Stylized "K" on the left side
    k_color = (242, 247, 252, 240)
    # Left vertical stem of K
    draw.rounded_rectangle([130, 120, 175, 392], radius=12, fill=k_color)
    
    # Upper diagonal of K
    draw.polygon([(175, 240), (285, 120), (335, 120), (205, 275)], fill=k_color)
    
    # Lower diagonal of K
    draw.polygon([(195, 255), (330, 392), (275, 392), (160, 275)], fill=k_color)

    # 4. Central Electric Lightning Bolt cutting across (Signal Cyan #20B8F2 -> Glow #85E4FF)
    bolt_points = [
        (295, 95),   # Top point
        (225, 245),  # Middle notch in
        (275, 245),  # Middle notch out
        (205, 415),  # Bottom point
        (270, 275),  # Return notch in
        (220, 275),  # Return notch out
    ]
    
    # Bolt Glow
    glow_img = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_draw.polygon(bolt_points, fill=(32, 184, 242, 220))
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(glow_img)

    # Main Bolt (Cyan to White)
    draw.polygon(bolt_points, fill=(32, 184, 242, 255), outline=(133, 228, 255, 255))
    
    # Inner Bright Core of Bolt
    inner_bolt = [
        (290, 115),
        (232, 248),
        (268, 248),
        (218, 395),
        (262, 278),
        (228, 278),
    ]
    draw.polygon(inner_bolt, fill=(255, 255, 255, 230))

    # 5. Save PNG
    png_path = os.path.join("resources", "icon.png")
    img.save(png_path, "PNG")
    print(f"Saved {png_path}")

    # 6. Save Multi-resolution Windows ICO
    ico_path = os.path.join("resources", "icon.ico")
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"Saved {ico_path} with sizes: {icon_sizes}")

if __name__ == "__main__":
    create_kayzit_icon()
