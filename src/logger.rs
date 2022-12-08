use colored::*;
use log::{Level, LevelFilter, Log, Metadata, Record, SetLoggerError};

pub struct SimpleLogger {
    /// The default logging level
    default_level: LevelFilter,
}

impl SimpleLogger {
    // pub fn new_default() -> SimpleLogger {
    //     SimpleLogger {
    //         default_level: LevelFilter::Warn,
    //     }
    // }

    pub fn new(max_level: LevelFilter) -> SimpleLogger {
        SimpleLogger {
            default_level: max_level,
        }
    }

    pub fn init(self) -> Result<(), SetLoggerError> {
        #[cfg(windows)]
        set_up_color_terminal();

        log::set_max_level(self.default_level);
        log::set_boxed_logger(Box::new(self))?;
        Ok(())
    }
}

impl Log for SimpleLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= self.default_level
    }

    fn log(&self, record: &Record) {
        if self.enabled(record.metadata()) {
            let level_string = {
                match record.level() {
                    Level::Error => format!("{:<5}", record.level().to_string())
                        .red()
                        .to_string(),
                    Level::Warn => format!("{:<5}", record.level().to_string())
                        .yellow()
                        .to_string(),
                    Level::Info => format!("{:<5}", record.level().to_string())
                        .cyan()
                        .to_string(),
                    Level::Debug => format!("{:<5}", record.level().to_string())
                        .purple()
                        .to_string(),
                    Level::Trace => format!("{:<5}", record.level().to_string())
                        .normal()
                        .to_string(),
                }
            };

            let target = if !record.target().is_empty() {
                record.target()
            } else {
                record.module_path().unwrap_or_default()
            };

            let message = format!("{} [{}] {}", level_string, target, record.args());

            // to switch to STDOUT
            // println!("{}", message);

            // to switch to STDERR
            eprintln!("{}", message);
        }
    }

    fn flush(&self) {}
}

#[cfg(windows)]
fn set_up_color_terminal() {
    use atty::Stream;

    if atty::is(Stream::Stdout) {
        unsafe {
            use windows_sys::Win32::Foundation::INVALID_HANDLE_VALUE;
            use windows_sys::Win32::System::Console::{
                GetConsoleMode, GetStdHandle, SetConsoleMode, CONSOLE_MODE,
                ENABLE_VIRTUAL_TERMINAL_PROCESSING, STD_OUTPUT_HANDLE,
            };

            let stdout = GetStdHandle(STD_OUTPUT_HANDLE);

            if stdout == INVALID_HANDLE_VALUE {
                return;
            }

            let mut mode: CONSOLE_MODE = 0;

            if GetConsoleMode(stdout, &mut mode) == 0 {
                return;
            }

            SetConsoleMode(stdout, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
        }
    }
}
