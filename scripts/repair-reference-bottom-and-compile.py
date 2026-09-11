from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# The V3 catalog owns the theme and campaign mapping. This late compatibility
# script must never rewrite those sections or assume the old campaign helper.
# Only ensure the reusable bottom item exists when MainShell already uses it.
if '_BottomItem extends StatelessWidget' not in s and 'bottomNavigationBar: Container(' in s:
    marker = 'class CampaignsPage extends StatefulWidget {'
    item = '''class _BottomItem extends StatelessWidget {
  final int index;
  final int current;
  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final VoidCallback onTap;

  const _BottomItem({
    required this.index,
    required this.current,
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final selected = index == current;
    final color = selected ? const Color(0xFF7C4DFF) : const Color(0xFF8A8494);
    return Expanded(
      child: InkWell(
        onTap: onTap,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(selected ? selectedIcon : icon, size: 21, color: color),
            const SizedBox(height: 3),
            Text(label, maxLines: 1, overflow: TextOverflow.ellipsis,
              style: TextStyle(fontSize: 10, fontWeight: selected ? FontWeight.w800 : FontWeight.w600, color: color)),
          ],
        ),
      ),
    );
  }
}

'''
    if marker in s:
        s = s.replace(marker, item + marker, 1)

p.write_text(s, encoding='utf-8')
print('Reference bottom compatibility repair applied without touching V3 theme or campaign mapping')
