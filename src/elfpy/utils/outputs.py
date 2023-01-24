"""
Helper functions for post-processing simulation outputs
"""
import os
import sys
import json
from typing import Optional
import logging
from logging.handlers import RotatingFileHandler

import numpy as np

import elfpy


def format_axis(
    axis_handle, xlabel="", fontsize=18, linestyle="--", linewidth="1", color="grey", which="both", axis="y"
):
    """Formats the axis"""
    # pylint: disable=too-many-arguments
    axis_handle.set_xlabel(xlabel)
    axis_handle.tick_params(axis="both", labelsize=fontsize)
    axis_handle.grid(visible=True, linestyle=linestyle, linewidth=linewidth, color=color, which=which, axis=axis)
    if xlabel == "":
        axis_handle.xaxis.set_ticklabels([])
    axis_handle.legend(fontsize=fontsize)


def annotate(axis_handle, text, major_offset, minor_offset, val):
    """Adds legend-like labels"""
    annotation_handle = axis_handle.annotate(
        text,
        xy=(
            val["position_x"],
            val["position_y"] - val["major_offset"] * major_offset - val["minor_offset"] * minor_offset,
        ),
        xytext=(
            val["position_x"],
            val["position_y"] - val["major_offset"] * major_offset - val["minor_offset"] * minor_offset,
        ),
        xycoords="subfigure fraction",
        fontsize=val["font_size"],
        alpha=val["alpha"],
    )
    annotation_handle.set_bbox(
        dict(facecolor="white", edgecolor="black", alpha=val["alpha"], linewidth=0, boxstyle="round,pad=0.1")
    )


def float_to_string(value, precision=3, min_digits=0, debug=False):
    """
    Format a float to a string with a given precision
    this follows the significant figure behavior, irrepective of number size
    """
    # TODO: Include more specific error handling in the except statement
    # pylint: disable=broad-except
    if debug:
        print(f"value: {value}, type: {type(value)}, precision: {precision}, min_digits: {min_digits}")
    if np.isinf(value):
        return "inf"
    if np.isnan(value):
        return "nan"
    if value == 0:
        return "0"
    try:
        digits = int(np.floor(np.log10(abs(value)))) + 1  #  calculate number of digits in value
    except Exception as err:
        if debug:
            print(
                f"Error in float_to_string: value={value}({type(value)}), precision={precision},"
                f" min_digits={min_digits}, \n error={err}"
            )
        return str(value)
    # decimals = np.clip(precision - digits, 0, precision)
    decimals = min(max(precision - digits, min_digits), precision)  #  calculate desired decimals
    if debug:
        print(f"value: {value}, type: {type(value)} calculated digits: {digits}, decimals: {decimals}")
    if abs(value) > 0.1:
        string = f"{value:,.{decimals}f}"
    else:  # add an additional sigfig if the value is really small
        string = f"{value:0.{precision-1}e}"
    return string


def delete_log_file() -> None:
    """If the logger's handler if a file handler, delete the underlying file."""
    handler = logging.getLogger().handlers[0]
    if isinstance(handler, logging.FileHandler):
        os.remove(handler.baseFilename)
    logging.getLogger().removeHandler(handler)


def setup_logging(
    log_filename: Optional[str] = None,
    max_bytes: int = elfpy.DEFAULT_LOG_MAXBYTES,
    log_level: int = elfpy.DEFAULT_LOG_LEVEL,
) -> None:
    """Setup logging and handlers with default settings"""
    if log_filename is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        log_dir, log_name = os.path.split(log_filename)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handler = RotatingFileHandler(os.path.join(log_dir, log_name), mode="w", maxBytes=max_bytes)
    logging.getLogger().setLevel(log_level)  # events of this level and above will be tracked
    handler.setFormatter(logging.Formatter(elfpy.DEFAULT_LOG_FORMATTER, elfpy.DEFAULT_LOG_DATETIME))
    logging.getLogger().addHandler(handler)  # assign handler to logging


def close_logging(delete_logs=True):
    """Close logging and handlers for the test"""
    logging.shutdown()
    if delete_logs:
        for handler in logging.getLogger().handlers:
            if hasattr(handler, "baseFilename") and not isinstance(handler, logging.StreamHandler):
                # access baseFilename in a type safe way
                handler_file_name = getattr(handler, "baseFilename")
                if os.path.exists(handler_file_name):
                    os.remove(handler_file_name)
            handler.close()


class CustomEncoder(json.JSONEncoder):
    """Custom encoder for JSON string dumps"""

    def default(self, o):
        """Override default behavior"""
        match o:
            case np.integer():
                return int(o)
            case np.floating():
                return float(o)
            case np.ndarray():
                return o.tolist()
            case _:
                try:
                    return o.__dict__
                except AttributeError:
                    return repr(o)
