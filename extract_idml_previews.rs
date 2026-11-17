use std::fs;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let indd_path = "/home/usuario/Descargas/pycode/indesign_forensics/target.indd";
    let bytes = fs::read(indd_path)?;
    let name = "target.indd";
    
    let conv = indd::convert(&bytes, name)?;
    println!("[+] Conversion completed! Previews count: {}", conv.previews.len());
    
    let out_dir = Path::new("/home/usuario/Descargas/pycode/indesign_forensics/extracted_previews");
    fs::create_dir_all(out_dir)?;
    
    for (i, p) in conv.previews.iter().enumerate() {
        let ext = if p.data.starts_with(b"\xff\xd8\xff") {
            "jpg"
        } else if p.data.starts_with(b"\x89PNG") {
            "png"
        } else if p.data.starts_with(b"GIF") {
            "gif"
        } else {
            "bin"
        };
        let file_name = format!("preview_{}_{}.{}", i, p.graphics.join("_"), ext);
        let out_path = out_dir.join(file_name);
        fs::write(&out_path, &p.data)?;
        println!("  Preview #{}: graphics={:?}, bytes={}, saved to {:?}", i, p.graphics, p.data.len(), out_path);
    }
    
    Ok(())
}
