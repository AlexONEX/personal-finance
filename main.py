#!/usr/bin/env python3
"""
main.py - Orquestador central del Ingresos Tracker.
Uso:
  python main.py --all          # Ejecuta fetch de datos y actualiza todas las sheets
  python main.py --fetch        # Solo descarga nuevos datos (CER, CCL, etc)
  python main.py --setup        # Re-aplica estructura y fórmulas (sin fetch)
  python main.py --since YYYY-MM-DD  # Fetch desde una fecha específica
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from fetch_data import main as fetch_main
from setup_sheet import setup_all

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Ingresos Tracker Manager")
    parser.add_argument("--all", action="store_true", help="Fetch data and update all sheets")
    parser.add_argument("--fetch", action="store_true", help="Only fetch new data")
    parser.add_argument("--setup", action="store_true", help="Only update sheet structure and formulas")
    parser.add_argument("--since", type=str, help="Start date for fetch (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    if not (args.all or args.fetch or args.setup):
        parser.print_help()
        return

    # 1. Fetch de datos
    if args.all or args.fetch:
        print("\n" + "="*50)
        print("1. INICIANDO FETCH DE DATOS (CER, CCL, REM, SPY)")
        print("="*50)
        # Mock sys.argv para fetch_data.main
        fetch_args = []
        if args.since:
            fetch_args.extend(["--since", args.since])
        
        # Guardamos sys.argv original
        old_argv = sys.argv
        sys.argv = ["fetch_data.py"] + fetch_args
        try:
            fetch_main()
        finally:
            sys.argv = old_argv

    # 2. Setup de estructura y fórmulas
    if args.all or args.setup:
        print("\n" + "="*50)
        print("2. ACTUALIZANDO ESTRUCTURA Y FÓRMULAS (ARRAYFORMULA)")
        print("="*50)
        setup_all()

    print("\n✅ Proceso completado exitosamente.")

if __name__ == "__main__":
    main()
