import 'package:flutter/material.dart';

class KKDesign {
  static const bg = Color(0xFFF7F8FF);
  static const text = Color(0xFF171A2B);
  static const muted = Color(0xFF686D82);
  static const primary = Color(0xFF5B4BDB);
  static const primaryDark = Color(0xFF3E2A9A);
  static const border = Color(0xFFE1E3F0);
  static const soft = Color(0xFFECEBFF);

  static ThemeData theme() => ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        colorScheme: ColorScheme.fromSeed(
          seedColor: primary,
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: bg,
        appBarTheme: const AppBarTheme(
          elevation: 0,
          scrolledUnderElevation: 0,
          backgroundColor: bg,
          foregroundColor: text,
        ),
        inputDecorationTheme: const InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(16)),
            borderSide: BorderSide(color: border),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(16)),
            borderSide: BorderSide(color: border),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(16)),
            borderSide: BorderSide(color: primary, width: 1.5),
          ),
        ),
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          surfaceTintColor: Colors.transparent,
        ),
      );

  static const gradient = LinearGradient(
    colors: [Color(0xFF7C6FF0), primaryDark],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

class KKLogo extends StatelessWidget {
  final double size;
  const KKLogo({super.key, this.size = 44});

  @override
  Widget build(BuildContext context) => Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          gradient: KKDesign.gradient,
          borderRadius: BorderRadius.circular(size * .28),
        ),
        child: Icon(
          Icons.credit_card_rounded,
          color: Colors.white,
          size: size * .58,
        ),
      );
}

class KKSectionTitle extends StatelessWidget {
  final String title;
  const KKSectionTitle(this.title, {super.key});

  @override
  Widget build(BuildContext context) => Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w900,
          color: KKDesign.text,
        ),
      );
}
