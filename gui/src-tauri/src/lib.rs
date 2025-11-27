use serde::{Deserialize, Serialize};
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Emitter, Manager, Runtime,
};

#[derive(Debug, Serialize, Deserialize)]
struct Bug {
    repo: String,
    issue_number: i32,
    title: String,
    url: String,
    impact_score: i32,
    affected_users: i32,
    severity: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ScanResult {
    bugs: Vec<Bug>,
    total_users: i32,
}

#[tauri::command]
async fn search_ecosystem(query: String, min_impact: i32) -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("bugnosis")
        .arg("search")
        .arg(&query)
        .arg("--min-impact")
        .arg(min_impact.to_string())
        .output()
        .map_err(|e| format!("Failed to execute bugnosis: {}", e))?;
    
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn get_saved_bugs(min_impact: i32) -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("bugnosis")
        .arg("list")
        .arg("--min-impact")
        .arg(min_impact.to_string())
        .arg("--json")
        .output()
        .map_err(|e| format!("Failed to execute bugnosis: {}", e))?;
    
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn get_stats() -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("bugnosis")
        .arg("stats")
        .output()
        .map_err(|e| format!("Failed to execute bugnosis: {}", e))?;
    
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn get_watched_repos() -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("bugnosis")
        .arg("watch")
        .arg("list")
        .output()
        .map_err(|e| format!("Failed to execute bugnosis: {}", e))?;
    
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn add_watched_repo(repo: String) -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("bugnosis")
        .arg("watch")
        .arg("add")
        .arg(&repo)
        .output()
        .map_err(|e| format!("Failed to execute bugnosis: {}", e))?;
    
    if output.status.success() {
        Ok(format!("Added {} to watch list", repo))
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn scan_watched() -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("bugnosis")
        .arg("watch")
        .arg("scan")
        .output()
        .map_err(|e| format!("Failed to execute bugnosis: {}", e))?;
    
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn get_insights(min_impact: i32) -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("bugnosis")
        .arg("insights")
        .arg("--min-impact")
        .arg(min_impact.to_string())
        .output()
        .map_err(|e| format!("Failed to execute bugnosis: {}", e))?;
    
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

#[tauri::command]
async fn check_online_status() -> bool {
    // Simple check: try to connect to 8.8.8.8:53
    use std::net::TcpStream;
    use std::time::Duration;
    
    match TcpStream::connect_timeout(
        &"8.8.8.8:53".parse().unwrap(), 
        Duration::from_millis(1500)
    ) {
        Ok(_) => true,
        Err(_) => false,
    }
}

fn setup_tray<R: Runtime>(app: &tauri::AppHandle<R>) -> tauri::Result<()> {
    let quit_i = MenuItem::with_id(app, "quit", "Quit Bugnosis", true, None::<&str>)?;
    let show_i = MenuItem::with_id(app, "show", "Show Window", true, None::<&str>)?;
    let scan_i = MenuItem::with_id(app, "scan", "Scan Watched Repos", true, None::<&str>)?;
    
    let menu = Menu::with_items(app, &[&show_i, &scan_i, &quit_i])?;
    
    let _tray = TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .on_menu_event(|app, event| match event.id.as_ref() {
            "quit" => {
                app.exit(0);
            }
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "scan" => {
                // Trigger scan in background
                let app_handle = app.clone();
                tauri::async_runtime::spawn(async move {
                    // Send notification
                    if let Some(window) = app_handle.get_webview_window("main") {
                        let _ = window.emit("trigger-scan", ());
                    }
                });
            }
            _ => {}
        })
        .build(app)?;
    
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            setup_tray(app.handle())?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            search_ecosystem,
            get_saved_bugs,
            get_stats,
            get_watched_repos,
            add_watched_repo,
            scan_watched,
            get_insights,
            check_online_status
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
