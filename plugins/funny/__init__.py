from core.plugin import load_mods

sub_plugins = load_mods(
  "funny",
  *["chat", "fortune", "hot", "poke", "repeater", "recorder", "sleep", "trace_moe"],
)
